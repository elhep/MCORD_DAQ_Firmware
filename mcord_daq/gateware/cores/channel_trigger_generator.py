from migen import *
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer


class ChannelTriggerGenerator(Module):

    def __init__(self, data_width):
        # CD: sys
        self.trigger_mode_i = Signal(11)
        self.trigger_level_i = Signal(data_width)

        # CD: dclk
        self.data_i = Signal(data_width)
        self.baseline_i = Signal(data_width)

        # CD: sys
        self.trigger_o = Signal()

        # # #

        # Mode[1:0]: 00 - trigger generator disabled
        # Mode[1:0]: 01 - rising edge
        # Mode[1:0]: 10 - falling edge
        # Mode[1:0]: 11 - both edges
        # Mode[2:2]:  0 - absolute
        # Mode[2:2]:  1 - wrt baseline
        # Mode[10:3]: counter limit

        self.clock_domains.cd_dclk = ClockDomain("dclk")

        trigger_level_dclk = Signal.like(self.trigger_level_i)
        trigger_level_cdc = BusSynchronizer(len(self.trigger_level_i), "sys", "dclk")
        self.submodules += trigger_level_cdc
        self.comb += [
            trigger_level_cdc.i.eq(self.trigger_level_i),
            trigger_level_dclk.eq(trigger_level_cdc.o)
        ]

        trigger_mode_dclk = Signal.like(self.trigger_level_i)
        trigger_mode_cdc = BusSynchronizer(len(self.trigger_level_i), "sys", "dclk")
        self.submodules += trigger_mode_cdc
        self.comb += [
            trigger_mode_cdc.i.eq(self.trigger_mode_i),
            trigger_mode_dclk.eq(trigger_mode_cdc.o)
        ]

        reference_level = Signal.like(self.data_i)
        self.comb += [
            If(~trigger_mode_dclk[2],
                reference_level.eq(self.trigger_level_i)
            ).Else(
                reference_level.eq(self.baseline_i)
            )
        ]

        reference_level_dclk = Signal.like(reference_level)
        reference_level_cdc = BusSynchronizer(len(self.trigger_level_i), "sys", "dclk")
        self.submodules += reference_level_cdc
        self.comb += [
            reference_level_cdc.i.eq(self.trigger_level_i),
            reference_level_dclk.eq(reference_level_cdc.o)
        ]

        counter_limit = Signal(8)
        counter = Signal(9)
        rising_edge = Signal()
        falling_edge = Signal()

        fsm = FSM("below")
        self.submodules += ClockDomainsRenamer("dclk")(fsm)

        fsm.act("below",
            NextValue(rising_edge, 0),
            NextValue(falling_edge, 0),
            If(self.data_i > reference_level_dclk,
                If(counter >= counter_limit,
                    NextValue(rising_edge, 1),
                    NextValue(counter, 0),
                    NextState("above")
                ).Else(
                    NextValue(counter, counter + 1),
                )
            ).Else(
                NextValue(counter, 0)
            )
        )
        fsm.act("above",
            NextValue(rising_edge, 0),
            NextValue(falling_edge, 0),
            If(self.data_i <= reference_level_dclk,
               If(counter >= counter_limit,
                  NextValue(falling_edge, 1),
                  NextValue(counter, 0),
                  NextState("below")
               ).Else(
                  NextValue(counter, counter + 1),
               )
           ).Else(
                NextValue(counter, 0)
            )
        )

        trigger_out_dclk = Signal()
        self.comb += [
            trigger_out_dclk.eq((trigger_mode_dclk[0] & rising_edge) | (trigger_mode_dclk[1] & falling_edge))
        ]

        trigger_out_cdc = PulseSynchronizer("dclk", "sys")
        self.submodules += trigger_out_cdc
        self.comb += [
            trigger_out_cdc.i.eq(trigger_out_dclk),
            self.trigger_o.eq(trigger_out_cdc.o)
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import *

    class SimulationWrapper(Module):
        def __init__(self):
            self.dclk_i = Signal()
            self.dclk_rst_i = Signal()
            self.submodules.dut = ChannelTriggerGenerator(16)
            self.comb += [self.dut.cd_dclk.clk.eq(self.dclk_i)]

    tb = SimulationWrapper()
    ios = get_ios(tb)
    ios = ios.union(get_ios(tb.dut))
    generate_verilog(tb, "dut.v", ios)
