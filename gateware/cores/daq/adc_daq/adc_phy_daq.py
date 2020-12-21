from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *


from migen import *
from migen.fhdl.specials import Memory
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer
from migen.fhdl import verilog
from artiq.gateware.rtio import rtlink

from functools import reduce
from operator import and_


class TriggerGenerator(Module):

    def __init__(self, data, trigger_level_rio_phy, treshold_length=4):

        # Outputs

        self.trigger_re = Signal()  # CD: rio_phy
        self.trigger_fe = Signal()  # CD: rio_phy

        # # #

        trigger_level_dclk = Signal.like(data)
        trigger_level_cdc = BusSynchronizer(len(data), idomain="rio_phy", odomain="sys")
        self.submodules += trigger_level_cdc
        self.comb += [
            trigger_level_cdc.i.eq(trigger_level_rio_phy),
            trigger_level_dclk.eq(trigger_level_cdc.o)
        ]

        data_prev_dclk = Signal(len(data)*treshold_length)

        above_comparison_list = [data_prev_dclk[i*len(data):(i+1)*len(data)] >= trigger_level_dclk for i in range(treshold_length)]
        below_comparison_list = [data_prev_dclk[i*len(data):(i+1)*len(data)] <= trigger_level_dclk for i in range(treshold_length)]
        data_above = Signal()
        data_below = Signal()

        self.comb += [
            data_above.eq(reduce(and_, above_comparison_list)),
            data_below.eq(reduce(and_, below_comparison_list))
        ]

        above_prev_dclk = Signal()
        below_prev_dclk = Signal()

        trigger_re_dclk = Signal()
        trigger_fe_dclk = Signal()

        self.sync.dclk += [
            data_prev_dclk.eq((data_prev_dclk << len(data)) | data),

            If(data_above & ~above_prev_dclk, trigger_re_dclk.eq(1)).Else(trigger_re_dclk.eq(0)),
            If(data_below & ~below_prev_dclk, trigger_fe_dclk.eq(1)).Else(trigger_fe_dclk.eq(0)),
            
            above_prev_dclk.eq(data_above),
            below_prev_dclk.eq(data_below)
        ]

        trigger_re_cdc = PulseSynchronizer(idomain="dclk", odomain="rio_phy")
        self.submodules += trigger_re_cdc
        self.comb += [
            trigger_re_cdc.i.eq(trigger_re_dclk),
            self.trigger_re.eq(trigger_re_cdc.o),
        ]

        trigger_fe_cdc = PulseSynchronizer(idomain="dclk", odomain="rio_phy")
        self.submodules += trigger_fe_cdc
        self.comb += [
            trigger_fe_cdc.i.eq(trigger_fe_dclk),
            self.trigger_fe.eq(trigger_fe_cdc.o),
        ]


class AdcPhyDaq(Module):
    """Data Acquisition Module

    :param data_clk: [CD: dclk] data clock signal
    :param data: [CD: dclk] data bus signal
    :param trigger_ext: [CD: rio_phy] external trigger signal
    :param max_samples: maximum length of acquisition (pretrigger+posttrigger)
    :param treshold_length: number of samples that need to be above/below trigger level
                            for the trigger to fire

    **CAUTION:** `max_samples` defines length of internal buffer, you must set 
    RTIO channel's `ififo_depth` to at least the same value to be able to transfer
    all samples.
    """

    def __init__(self, data_clk, data, trigger_ext=None, max_samples=1024, treshold_length=4):
        
        # Outputs

        self.trigger_re = Signal()  # CD: rio_phy
        self.trigger_fe = Signal()  # CD: rio_phy

        # # #

        # --------------------------------------------------------------------------------------------------------------
        # Sample memory

        assert max_samples <= 2**12-1

        memory = Memory(len(data), max_samples, init=[0]*max_samples)
        memory_write_port = memory.get_port(write_capable=True, clock_domain="dclk")
        memory_read_port = memory.get_port(has_re=True, clock_domain="rio_phy")
        self.specials += [ memory, memory_write_port, memory_read_port ]

        # --------------------------------------------------------------------------------------------------------------
        # Acquisition control

        trigger_dclk = Signal()

        pretrigger_len_dclk = Signal(12, reset=16)
        posttrigger_len_dclk = Signal(12, reset=16)
        current_address_dclk = Signal.like(memory_write_port.adr, reset=0)
        data_start_address_dclk = Signal.like(current_address_dclk)
        data_start_address_reg_dclk = Signal.like(data_start_address_dclk)
        posttrigger_counter_dclk = Signal(max=max_samples)
        transfer_en_dclk = Signal()
        transfer_done_dclk = Signal()
        
        self.sync.dclk += [
            # We need to wrap current_address when buffer_depth is reached
            If(current_address_dclk == max_samples-1,
               current_address_dclk.eq(0)).
            Else(
               current_address_dclk.eq(current_address_dclk+1)),
        ]

        self.comb += [
            memory_write_port.adr.eq(current_address_dclk),
            memory_write_port.dat_w.eq(data),
            # Compute start address for further readout
            If(current_address_dclk < pretrigger_len_dclk,
                data_start_address_dclk.eq(max_samples + current_address_dclk - pretrigger_len_dclk)).
            Else(
                data_start_address_dclk.eq(current_address_dclk - pretrigger_len_dclk)),
        ]

        # Data clock side FSM

        fsm_dclk = ClockDomainsRenamer("dclk")(FSM("PRETRIGGER"))
        self.submodules.fsm_dclk = fsm_dclk

        fsm_dclk.act("PRETRIGGER",
                memory_write_port.we.eq(1),
                If(trigger_dclk,
                   NextValue(data_start_address_reg_dclk, data_start_address_dclk),
                   If(posttrigger_len_dclk != 0,
                       NextValue(posttrigger_counter_dclk, posttrigger_len_dclk),
                       NextState("POSTTRIGGER")).
                   Else(
                       NextState("TRANSFER"),
                       NextValue(transfer_en_dclk, 1))
                ))
        fsm_dclk.act("POSTTRIGGER",
                memory_write_port.we.eq(1),
                NextValue(posttrigger_counter_dclk, posttrigger_counter_dclk-1),
                If(posttrigger_counter_dclk == 0,
                   NextState("TRANSFER"),
                   NextValue(transfer_en_dclk, 1))
                )
        fsm_dclk.act("TRANSFER",
                memory_write_port.we.eq(0),
                NextValue(transfer_en_dclk, 0),
                If(transfer_done_dclk,
                   NextState("PRETRIGGER"))
                )
        
        # --------------------------------------------------------------------------------------------------------------
        # RTLink support

        # Address map:
        #  0: direct trigger [0]
        #  1: pretrigger[23:12], posttrigger[11:0]
        #  2: trigger_level [9:0]

        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=24, address_width=3),
            rtlink.IInterface(data_width=10, timestamped=True))

        trigger_combined_rio_phy = Signal()
        trigger_rtlink_rio_phy = Signal()
        trigger_level_rio_phy = Signal.like(data)
        pretrigger_len_rio_phy = Signal.like(pretrigger_len_dclk)
        posttrigger_len_rio_phy = Signal.like(posttrigger_counter_dclk)
        transfer_done_rio_phy = Signal()
        data_start_address_reg_rio_phy = Signal.like(data_start_address_reg_dclk)
        transfer_en_rio_phy = Signal()
        counter_rio_phy = Signal.like(memory_read_port.adr)

        self.sync.rio_phy += [
            trigger_rtlink_rio_phy.eq(0),
            If(self.rtlink.o.stb,
               If(self.rtlink.o.address == 0, trigger_rtlink_rio_phy.eq(1)),
               If(self.rtlink.o.address == 1, Cat(pretrigger_len_rio_phy, posttrigger_len_rio_phy).eq(self.rtlink.o.data[0:24])),
               If(self.rtlink.o.address == 2, trigger_level_rio_phy.eq(self.rtlink.o.data[0:len(data)]))
            )
        ]

        self.comb += self.rtlink.i.data.eq(memory_read_port.dat_r)

        if trigger_ext is not None:
            self.comb += trigger_combined_rio_phy.eq(trigger_rtlink_rio_phy | trigger_ext)
        else:
            self.comb += trigger_combined_rio_phy.eq(trigger_rtlink_rio_phy)

        # --------------------------------------------------------------------------------------------------------------
        # Sample transfer to RTLink

        fsm_rio_phy = ClockDomainsRenamer("rio_phy")(FSM("IDLE"))
        self.submodules.fsm_rio_phy = fsm_rio_phy

        fsm_rio_phy.act("IDLE",
                memory_read_port.re.eq(0),
                NextValue(transfer_done_rio_phy, 0),
                NextValue(self.rtlink.i.stb, 0),
                If(transfer_en_rio_phy,
                   NextValue(memory_read_port.adr, data_start_address_reg_rio_phy),
                   NextValue(counter_rio_phy, 0),
                   NextState("TRANSFER"))
                )
        fsm_rio_phy.act("TRANSFER",
                memory_read_port.re.eq(1),
                NextValue(counter_rio_phy, counter_rio_phy+1),
                NextValue(self.rtlink.i.stb, 1),
                If(memory_read_port.adr+1 >= max_samples,
                   NextValue(memory_read_port.adr, 0))
                .Else(NextValue(memory_read_port.adr, memory_read_port.adr+1)),
                If(counter_rio_phy == (pretrigger_len_rio_phy + posttrigger_len_rio_phy - 1),
                   NextState("IDLE"),
                   NextValue(transfer_done_rio_phy, 1))
                )

        # --------------------------------------------------------------------------------------------------------------
        # Trigger generator

        trigger_generator = ClockDomainsRenamer("dclk")(TriggerGenerator(data, trigger_level_rio_phy, treshold_length))
        self.submodules += trigger_generator
        self.comb += [
            self.trigger_re.eq(trigger_generator.trigger_re),
            self.trigger_fe.eq(trigger_generator.trigger_fe)
        ]

        # --------------------------------------------------------------------------------------------------------------
        # CDC dclk -> rio_phy

        self.comb += [data_start_address_reg_rio_phy.eq(data_start_address_reg_dclk)]
        cdc_transfer_en_dclk_rio_phy = PulseSynchronizer(idomain="dclk", odomain="rio_phy")
        self.submodules.cdc_transfer_en_dclk_rio_phy = cdc_transfer_en_dclk_rio_phy
        self.comb += [
            cdc_transfer_en_dclk_rio_phy.i.eq(transfer_en_dclk),
            transfer_en_rio_phy.eq(cdc_transfer_en_dclk_rio_phy.o)
        ]

        # --------------------------------------------------------------------------------------------------------------
        # CDC rio_phy -> dclk

        cdc_rio_phy_dclk = BusSynchronizer(24, idomain="rio_phy", odomain="dclk")
        self.submodules.cdc_rio_phy_dclk = cdc_rio_phy_dclk
        self.comb += [
            cdc_rio_phy_dclk.i.eq(Cat(pretrigger_len_rio_phy, posttrigger_len_rio_phy)),
            Cat(pretrigger_len_dclk, posttrigger_len_dclk).eq(cdc_rio_phy_dclk.o)
        ]
        cdc_trigger_rio_phy_dclk = PulseSynchronizer(idomain="rio_phy", odomain="dclk")
        self.submodules.cdc_trigger_rio_phy_dclk = cdc_trigger_rio_phy_dclk
        self.comb += [
            cdc_trigger_rio_phy_dclk.i.eq(trigger_combined_rio_phy),
            trigger_dclk.eq(cdc_trigger_rio_phy_dclk.o)
        ]
        cdc_transfer_done_rio_phy_dclk = PulseSynchronizer(idomain="rio_phy", odomain="dclk")
        self.submodules.cdc_transfer_done_rio_phy_dclk = cdc_transfer_done_rio_phy_dclk
        self.comb += [
            cdc_transfer_done_rio_phy_dclk.i.eq(transfer_done_rio_phy),
            transfer_done_dclk.eq(cdc_transfer_done_rio_phy_dclk.o)
        ]

        # Debug signals

        trigger_dclk.attr.add(("mark_debug", "true"))
        trigger_combined_rio_phy.attr.add(("mark_debug", "true"))
        current_address_dclk.attr.add(("mark_debug", "true"))
        transfer_en_rio_phy.attr.add(("mark_debug", "true"))

        trigger_rtlink_rio_phy.attr.add(("mark_debug", "true"))
        transfer_done_rio_phy.attr.add(("mark_debug", "true"))

        self.rtlink.o.stb.attr.add(("mark_debug", "true"))
        self.rtlink.o.address.attr.add(("mark_debug", "true"))
        self.rtlink.o.data.attr.add(("mark_debug", "true"))
        self.rtlink.i.data.attr.add(("mark_debug", "true"))
        self.rtlink.i.stb.attr.add(("mark_debug", "true"))

        memory_read_port.adr.attr.add(("mark_debug", "true"))
        memory_read_port.dat_r.attr.add(("mark_debug", "true"))
        memory_read_port.re.attr.add(("mark_debug", "true"))

        memory_write_port.adr.attr.add(("mark_debug", "true"))
        memory_write_port.dat_w.attr.add(("mark_debug", "true"))
        memory_write_port.we.attr.add(("mark_debug", "true"))


class SimulationWrapper(Module):

    def __init__(self):

        self.data_clk = Signal()
        self.data = Signal(10)

        trigger_ext = Signal()

        self.clock_domains.cd_rio_phy = cd_rio_phy = ClockDomain()
        self.clock_domains.cd_dclk = cd_dclk = ClockDomain()

        self.comb += [cd_dclk.clk.eq(self.data_clk)]

        self.submodules.dut = dut = AdcPhyDaq(self.data_clk, self.data,  2048)

        self.io = {
            cd_dclk.rst,
            self.data_clk,
            self.data,
            trigger_ext,
            dut.trigger_fe,
            dut.trigger_re,
            cd_rio_phy.clk,
            cd_rio_phy.rst,
            dut.rtlink.i.stb,
            dut.rtlink.i.data,
            dut.rtlink.o.stb,
            dut.rtlink.o.address,
            dut.rtlink.o.data
        }


if __name__ == "__main__":

    from migen.build.xilinx import common
    from gateware.simulation.common import update_tb

    module = SimulationWrapper()
    # so = dict(common.xilinx_special_overrides)
    # so.update(common.xilinx_s7_special_overrides)

    verilog.convert(fi=module,
                    name="top",
                    # special_overrides=so,
                    ios=module.io,
                    create_clock_domains=False).write("adc_phy_daq.v")
    update_tb("adc_phy_daq.v")