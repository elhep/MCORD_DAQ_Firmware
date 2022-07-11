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

from elhep_cores.cores.trigger_generators import TriggerGenerator, \
    RtioCoincidenceTriggerGenerator, RtioTriggerGenerator
from elhep_cores.cores.rtlink_csr import RtLinkCSR
from elhep_cores.helpers.ddb_manager import HasDdbManager
from elhep_cores.simulation.common import update_tb
from elhep_cores.cores.xilinx_ila import ILAProbe


## stare nie aktualne
# Dane w postaci wartosci countera przychodza z n kanalow (10 bitow)
# jest zrobiona macierz i maska, ktore kanaly maja byc brane pod uwage
# Ustawialne Tmin pomiedzy probkami (od 0 do X)
# Ustawialne Tmax pomiedzy probkami (od X do 7?)
# Generowany trigger jako wyjscie 

# Otrzymuje wartosc counter jako wejscie kanalu - 32 bity 
# sprawdzam 


# liczba kanalow wejsciowych
# liczba wyjsc - kazde wyjscie ma jedna maske 

## System paczek
# Paczka wchodzi przez RTIOLink, synchronizacja przez słowo 0x1ACFFC1D
# Jeżeli początek 

class CollectorPacket:
    def __init__(self, ID=0, SystemTimestamp=0, TDCSample=0,
        StatisticalValues=0, ADCSamples = 0):
        # ID of the source channel, 10b
        # System Timestamp, together with source channel ID will act as event ID, 64b
        # T x TDC sample (T ideally should be 2, one per scintillator end, may be more if CFD is not configured properly, assume at most 10), 440b
        # Statistical values (imulse integral, imulse length), 20b+10b = 30b
        # Optional ADC samples, up to 200 10b values per event, 200*10 = 200b

        self.ID = Signal(10).eq(ID)
        self.SystemTimestamp = Signal(64).eq(SystemTimestamp)
        self.TDCSample = Signal(440).eq(TDCSample)
        self.StatisticalValues = Signal(30).eq(StatisticalValues)
        self.ADCSamples = Signal(200).eq(ADCSamples)

## Input mask in form of 0x3FF, if correct 
class CollectorGroup:
    def __init__(self, InputMask, ValidTopBits):
        self.InputMask = Signal(10).eq(InputMask)
        self.ValidTopBits = ValidTopBits
        self.Triggered = Signal().eq(0)
        self.Packet = CollectorPacket()

    def AssignPacket(self, Packet):
        self.Packet = Packet





class TriggerCollector(Module, HasDdbManager):

    def __init__(self, input_channels=2, groups=2, outputs=1, 
            module_identifier="trigger_collector"):
        self.module_identifier = module_identifier

        # Trigger reset 
        self.trigger_collector_reset = Signal()
        phy = Output(self.trigger_collector_reset)
        self.submodules.reset_phy = phy
        self.add_rtio_channels(
                channel=Channel.from_phy(phy),
                device_id=f"{module_identifier}_trigger_collector_reset",
                module="artiq.coredevice.ttl",
                class_name="TTLOut")

        self.outputs = outputs

        self.ChannelGroups = [CollectorGroup(0) for i in range(groups)]


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
        # Address 1: pulse length
        # Address 2: mask

        # self.mask = Signal(len(self.outputs))

        # mask_adr_no = (len(self.mask)+31)//32
        adr_width = len(Signal(max=3+1))+2

        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=32, address_width=adr_width))

        self.rtlink_address = rtlink_address = Signal.like(self.rtlink.o.address)
        self.rtlink_wen = rtlink_wen = Signal()
        self.comb += [
            rtlink_address.eq(self.rtlink.o.address[1:]),
            rtlink_wen.eq(self.rtlink.o.address[0]),
        ]

        RowsNum = 5

        self.DataShift = Array(Signal(32) for i in range(RowsNum))
        # mask_array = self.signal_to_array(self.mask)

        self.sync.rio_phy += [
            # self.rtlink.i.stb.eq(0),
            If(self.rtlink.o.stb,
                # Write
                If(rtlink_wen & (rtlink_address == 0),
                    # (for i in range(RowsNum):
                    self.DataShift[0].eq(self.rtlink.o.data)

                )
                # ).
                # Elif(rtlink_wen & (rtlink_address == 1),
                #     self.pulse_length.eq(self.rtlink.o.data)
                # )
                # Elif(rtlink_wen & (rtlink_address >= 2),
                #     mask_array[rtlink_address-2].eq(self.rtlink.o.data)
                # ).
                # Readout
                # Elif(~rtlink_wen & (rtlink_address == 0),
                #     self.rtlink.i.data.eq(self.enabled),
                #     self.rtlink.i.stb.eq(1)
                # ).
                # Elif(~rtlink_wen & (rtlink_address == 1),
                #     self.rtlink.i.data.eq(self.pulse_length),
                #     self.rtlink.i.stb.eq(1)
                # )
                # Elif(~rtlink_wen & (rtlink_address >= 2),
                #     self.rtlink.i.data.eq(mask_array[rtlink_address-2]),
                #     self.rtlink.i.stb.eq(1)
                # )
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

class SimulationWrapper(Module):

    def __init__(self):
        input_channels = 2
        outputs = 1

        # trigger_id_len = 1 + trigger_counter_len

        self.clock_domains.rio_phy = cd = ClockDomain()

        # trigger_generators = []
        # trigger_signals = []
            
        # outputs = [
        # {
        #     "label": f"output_{idx}", 
        #         "trigger": Signal(name=f"trigger_out_{idx}", reset=0), 
        #         "trigger_id": Signal(
        #             trigger_id_len, 
        #             name=f"trigger_out_id_{idx}",
        #             reset=0
        #         )
        #     } for idx in range(4) 
        # ]
        # output_triggers = [o['trigger'] for o in outputs]

        dut = TriggerCollector(
            input_channels, 
            outputs
        )
        self.submodules.dut = dut

        self.io = {
            cd.clk,
            cd.rst,
            *(get_bus_signals(dut.reset_phy.rtlink, "reset_phy_rtio")),
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
