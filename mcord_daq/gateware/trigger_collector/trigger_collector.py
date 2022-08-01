from functools import reduce
from operator import or_, and_
import json

from migen import *
from migen.fhdl import *
from migen.fhdl.specials import Memory

from migen.genlib.coding import PriorityEncoder
from migen.genlib.io import DifferentialInput
from migen.fhdl import verilog

from artiq.gateware.rtio import rtlink
from artiq.gateware.rtio.channel import Channel
from artiq.gateware.rtio.phy.ttl_simple import Output

from elhep_cores.cores.rtlink_csr import RtLinkCSR
from elhep_cores.helpers.ddb_manager import HasDdbManager
from elhep_cores.simulation.common import update_tb
from elhep_cores.cores.xilinx_ila import ILAProbe

## Packet Trigger Design
# In principle packet arrives via RTLink,
# Synchronization is necessary, proposition to use 0x1ACFFC1D or part of it (3 x 32 bits)

#TODO: TB and RTLink wrapper for data input

class CollectorPacket:
    def __init__(self, ID, SystemTimestamp, TDCSample,
        StatisticalValues, ADCSamples = 0):
        # ID of the source channel, 10b
        # System Timestamp, together with source channel ID will act as event ID, 64b
        # T x TDC sample (T ideally should be 2, one per scintillator end, may be more if CFD is not configured properly, assume at most 10), 440b
        # Statistical values (imulse integral, imulse length), 20b+10b = 30b
        # Optional ADC samples, up to 200 10b values per event, 200*10 = 200b

        # EDIT: 14.07.2022 - decision to limit full transaction to two 32-bit words
        # We are only using ID and SystemTimestamp - together 64bits

        # EDIT: 01.08.2022 - back to 3 words, with sync bits - together 96 bits

        self.ID = Signal(10) ## previous 10 
        self.SystemTimestamp = Signal(64) ## previous 64
        self.TDCSample = Signal(440)
        self.StatisticalValues = Signal(30)
        self.ADCSamples = Signal(200)
        
        self.ID.eq(ID)
        self.SystemTimestamp.eq(SystemTimestamp)
        self.TDCSample.eq(TDCSample)
        self.StatisticalValues.eq(StatisticalValues)
        self.ADCSamples.eq(ADCSamples)

## Input mask in form of 0x3FF, if correct 
class CollectorGroup:
    def __init__(self, InputMask, ValidMask):
        self.InputMask = Signal(10)
        self.InputMask.eq(InputMask)
        self.ValidMask = Signal(10)
        self.ValidMask.eq(ValidMask)
        self.Triggered = Signal(1, reset=1)
        self.Triggered.eq(1)

        self.Packet = CollectorPacket(0, 0, 0xdeadbeef, 0, 0)

    def AssignPacket(self, Packet):
        self.Packet = Packet

class CollectorConfig:
    def __init__(self, Tmax=0):
        # Minimum time between samples
        self.Tmax = Tmax



class TriggerCollector(Module, HasDdbManager):
    def _add_output(self, MainTrigger):

        trigger_or = Signal()
        trigger_or_prev = Signal()
        trigger = Signal()

        # self.comb += trigger_or.eq(channel_trigger)
        self.comb += trigger_or.eq(MainTrigger)

        self.sync.rio_phy += [
            trigger_or_prev.eq(trigger_or),
            If(self.trigger_collector_reset, trigger.eq(0))
            .Else(trigger.eq(trigger_or & ~trigger_or_prev))
        ]

        return trigger

    def __init__(self, groups=2, 
            module_identifier="trigger_collector"):
        self.module_identifier = module_identifier

        assert groups >= 2, f"Must be at least 2 groups! " 

        # Trigger reset 
        self.trigger_collector_reset = Signal()
        phy = Output(self.trigger_collector_reset)
        self.submodules.reset_phy = phy
        self.add_rtio_channels(
                channel=Channel.from_phy(phy),
                device_id=f"{module_identifier}_trigger_collector_reset",
                module="artiq.coredevice.ttl",
                class_name="TTLOut")

        self.Enabled = Signal()
        self._add_rtlink()

        self.InputPackets = [CollectorPacket(0, 0, 0, 0) for i in range(groups)]
        self.ChannelPackets = [CollectorGroup(0x3FF, 0x3FF) for i in range(groups)]
        self.WriteSignals = Signal(groups)

        for i in range(groups):
            self.sync.rio_phy += [
                    If(self.Enabled == 1, 
                        If(self.WriteSignals[i] == 1,
                            self.ChannelPackets[i].Triggered.eq(0),
                            self.ChannelPackets[i].Packet.ID.eq(self.InputPackets[i].ID),
                            self.ChannelPackets[i].Packet.SystemTimestamp.eq(self.InputPackets[i].SystemTimestamp),
                        )
                    )
            ]

        TriggeredCon = Signal(groups, reset=2**groups-1)
        
        for i in range(groups):
            self.sync.rio_phy += [
                TriggeredCon[i].eq(self.ChannelPackets[i].Triggered)
            ]

        SubstractionRes = [Signal.like(self.ChannelPackets[0].Packet.SystemTimestamp) for i in range(groups - 1)]
        SubstractionTrig = Signal(groups-1)

        TriggerTimeThreshold = self.Tmax

        self.PacketTrigger = Signal()

        for i in range(groups - 1):
            self.sync.rio_phy += [
                If(self.ChannelPackets[0].Packet.SystemTimestamp >= self.ChannelPackets[i+1].Packet.SystemTimestamp,
                SubstractionRes[i].eq(self.ChannelPackets[0].Packet.SystemTimestamp - self.ChannelPackets[i+1].Packet.SystemTimestamp))
                .Else(SubstractionRes[i].eq(self.ChannelPackets[i+1].Packet.SystemTimestamp - self.ChannelPackets[0].Packet.SystemTimestamp)),
                
                If(SubstractionRes[i] < TriggerTimeThreshold, SubstractionTrig[i].eq(1))
                .Else(SubstractionTrig[i].eq(0)),
            ]
            
        self.comb += [
            If((SubstractionTrig == (2**(groups - 1) - 1)), 
                If(TriggeredCon == 0, self.PacketTrigger.eq(1)))
            .Else(self.PacketTrigger.eq(0))
        ]

        for i in range(groups):
            self.sync.rio_phy += [
                If(self.Enabled==1, 
                    If(self.PacketTrigger==1, self.ChannelPackets[i].Triggered.eq(1))
                )
            ]

        self.Trigger = self._add_output(self.PacketTrigger)


        # # Register core device
        # self.register_coredevice(module_identifier, "mcord_daq.coredevice.trigger_collector", "TriggerCollector", arguments={
        #     "prefix": module_identifier,
        #     "l0_num": l0_num,
        #     "l1_num": l1_num,
        #     "output_config_csr": f"{module_identifier}_output_config",
        #     "l1_mask": trigger_labels,
        #     "reset_device": f"{module_identifier}_trigger_controller_reset"
        # })

        # self._add_rtlink()        


    def _add_rtlink(self):
        # Address 0: enabled
        # Address 1: Tmax
        # Address 2: mask

        # self.mask = Signal(len(self.outputs))

        # mask_adr_no = (len(self.mask)+31)//32
        adr_width = len(Signal(max=3+1))+2

        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=32, address_width=adr_width),
            rtlink.IInterface(data_width=32, timestamped=True))

        self.rtlink_address = rtlink_address = Signal.like(self.rtlink.o.address)
        self.rtlink_wen = rtlink_wen = Signal()
        self.comb += [
            rtlink_address.eq(self.rtlink.o.address[1:]),
            rtlink_wen.eq(self.rtlink.o.address[0]),
        ]

        # RowsNum = 5

        # self.DataShift = Array(Signal(32) for i in range(RowsNum))
        # mask_array = self.signal_to_array(self.mask)

        self.Tmax = Signal(32)

        self.sync.rio_phy += [
            If(self.rtlink.o.stb,
                # Write
                If(rtlink_wen & (rtlink_address == 0),
                    self.Enabled.eq(self.rtlink.o.data)
                ).
                Elif(rtlink_wen & (rtlink_address == 1),
                    self.Tmax.eq(self.rtlink.o.data)
                ).
                # Readout
                Elif(~rtlink_wen & (rtlink_address == 0),
                    self.rtlink.i.data.eq(self.Enabled),
                    self.rtlink.i.stb.eq(1)
                ).
                Elif(~rtlink_wen & (rtlink_address == 1),
                    self.rtlink.i.data.eq(self.Tmax),
                    self.rtlink.i.stb.eq(1)
                )
            )
        ]
        
def get_bus_signals(bus, bus_name="rtio"):
    signals = []
    def add_interface(iface, prefix):
        signals.append(iface.stb)
        iface.stb.name_override = f"{prefix}_stb"
        signals.append(iface.data)
        iface.data.name_override = f"{prefix}_data"
        if hasattr(iface, "address"):
            signals.append(iface.address)
            iface.address.name_override = f"{prefix}_address"
            
    add_interface(bus.o, f"{bus_name}_o")
    if bus.i is not None:
        add_interface(bus.i, f"{bus_name}_i")
    
    return signals

class RTTriggerCollector(Module, HasDdbManager):
    def __init__(self, groups=2, module_identifier="trigger_collector"):
        self.module_identifier = module_identifier

        self.clock_domains.cd_rio_phy = cd_rio_phy = ClockDomain()

        self.submodules.TriggerCollector = self.TriggerCollector = TriggerCollector(groups, module_identifier)
        self.Trigger = self.TriggerCollector.Trigger
        

        self.rtlink = self.TriggerCollector.rtlink

        self._add_rtlink_input(groups)

        self.Counters = []
        
        for i in range(groups):
            self.Counters += [Signal(max=3, reset=0)]
        # print(self.Counters[0])

        SyncValue = 0x1ACFFC1D
        

        for i in range(groups):
            self.sync.rio_phy += [
                
                If(self.rtlink_input[i].o.stb  == 1, 
                    If(self.rtlink_input[i].o.data[:22] == SyncValue>>(10),
                        self.Counters[i].eq(1),
                        self.TriggerCollector.WriteSignals[i].eq(0),
                        self.TriggerCollector.InputPackets[i].ID.eq(self.rtlink_input[i].o.data[22:]),
                    ).
                    Elif(self.Counters[i] == 1,
                        
                        self.TriggerCollector.InputPackets[i].SystemTimestamp.eq(self.rtlink_input[i].o.data),
                        self.Counters[i].eq(2),
                    ).
                    Elif(self.Counters[i] == 2,
                        self.TriggerCollector.InputPackets[i].SystemTimestamp.eq(self.rtlink_input[i].o.data<<32 | self.TriggerCollector.InputPackets[i].SystemTimestamp),
                        self.TriggerCollector.WriteSignals[i].eq(1),
                        self.Counters[i].eq(0),
                    )
                ).
                Else(
                    self.TriggerCollector.WriteSignals[i].eq(0),
                )
            ]



        
    def _add_rtlink_input(self, groups):
        # adr_width = len(Signal(max=3+1))+2
        self.rtlink_input = []
        for i in range(groups):
            self.rtlink_input += [rtlink.Interface(
                rtlink.OInterface(data_width=32))
            ]

class SimulationWrapper(Module):

    def __init__(self):
        # input_channels = 2
        groups = 2


        # trigger_id_len = 1 + trigger_counter_len

        self.clock_domains.rio_phy = cd = ClockDomain()

        dut = RTTriggerCollector( 
            groups
        )
        self.submodules.dut = dut

        self.io = {
            cd.clk,
            cd.rst,
            *(get_bus_signals(dut.TriggerCollector.reset_phy.rtlink, "reset_phy_rtio")),
            *(get_bus_signals(dut.rtlink, "config_rtio")),
            *(get_bus_signals(dut.rtlink_input[0], "input_rtio_0")),
            *(get_bus_signals(dut.rtlink_input[1], "input_rtio_1")),
            dut.Trigger,
        }

if __name__ == "__main__":

    from migen.build.xilinx import common
    from elhep_cores.simulation.common import update_tb

    module = SimulationWrapper()
    so = dict(common.xilinx_special_overrides)
    so.update(common.xilinx_s7_special_overrides)

    verilog.convert(fi=module,
                    name="top",
                    special_overrides=so,
                    ios=module.io,
                    create_clock_domains=False).write('dut.v')
    update_tb('dut.v')
