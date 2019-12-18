from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *
from ..common import *


class SimulationWrapper(Module):

    def __init__(self, platform, max_frame_length):
        self.submodules.dut = dut = LvdsSerialInterface(max_frame_length=max_frame_length, frame_idelay=False)
        self.submodules += XilinxIdelayctrl(platform.request("ref_clk_200MHz"))
        self.comb += [
            dut.data_clk_i.eq(platform.request("data_clk_i")),
            dut.frame_i.eq(platform.request("frame_i")),
            dut.data_i.eq(platform.request("data_i")),
            dut.frame_length_i.eq(platform.request("frame_length_i")),
            platform.request("data_o").eq(dut.data_o),
            platform.request("stb_o").eq(dut.stb_o)
        ]


class LvdsSerialInterface(Module):

    def __init__(self, max_frame_length, frame_idelay=False):

        # Interface definition
        # ==========================================

        # Hardware signals
        self.data_clk_i = Signal()
        self.frame_i = Signal()
        self.data_i = Signal()

        # Outputs
        self.data_o = Signal(max_frame_length)
        self.stb_o = Signal()

        # Config
        self.frame_length_i = Signal(max=max_frame_length)

        # Design
        # ==========================================

        self.clock_domains.sys = ClockDomain()
        self.comb += [self.sys.clk.eq(~self.data_clk_i)]

        frame = Signal(2)
        frame_in = Signal()
        if frame_idelay:
            self.submodules += XilinxIdelayE2(self.frame_i, frame_in)
            # TODO: Add frame checking logic
        else:
            frame_in = self.frame_i

        self.sync += [frame.eq(frame << 1 | frame_in)]
        frame_start = Signal()
        self.comb += frame_start.eq(frame[0] & ~frame[1])

        data = Signal()
        self.submodules += XilinxIdelayE2(self.data_i, data)

        data_q1 = Signal()
        data_q2 = Signal()
        data_q1q2 = Signal(2)
        self.submodules += XilinxDDRInputImplS7(i=data, o1=data_q2, o2=data_q1, clk=ClockSignal(),
                                                clk_edge="SAME_EDGE_PIPELINED")
        self.comb += data_q1q2.eq(Cat(data_q1, data_q2))

        shift_register = Signal(max_frame_length)
        shift_register_reg = Signal.like(shift_register)
        stb_reg = Signal()
        bit_counter = Signal(max=max_frame_length)
        self.submodules.fsm = fsm = FSM(reset_state="IDLE")
        fsm.act("IDLE",
                NextValue(bit_counter, self.frame_length_i),
                NextValue(stb_reg, 0),
                If(frame_start,
                   NextState("FRAMEACQ")
                )
        )
        fsm.act("FRAMEACQ",
                NextValue(bit_counter, bit_counter-2),
                NextValue(stb_reg, 0),
                If(bit_counter == 0,
                   NextValue(shift_register_reg, shift_register),
                   NextValue(stb_reg, 1),
                   If(frame_start,
                      NextValue(bit_counter, self.frame_length_i)
                   ).Else(
                       NextState("IDLE"))
                )
        )

        self.sync += [
            shift_register.eq((shift_register << 2) | data_q1q2)
        ]

        self.comb += [
            self.data_o.eq(shift_register_reg),
            self.stb_o.eq(stb_reg)
        ]


class Platform(XilinxPlatform):
    # default_clk_name = "clk"

    def __init__(self, frame_length):
        XilinxPlatform.__init__(self, "xc7", [
            # ("clk", 0, Pins("X")),
            ("data_clk_i", 0, Pins("X")),
            ("ref_clk_200MHz", 0, Pins("X")),
            ("frame_i", 0, Pins("X")),
            ("data_i", 0, Pins("X")),
            ("data_o", 0, Pins(" ".join(["X"]*frame_length))),
            ("stb_o", 0, Pins("X")),
            ("frame_length_i", 0, Pins(" ".join(['X']*6)))
        ])


if __name__ == "__main__":
    # Generate simulation source for Cocotb
    from design.simulation.common import generate_cocotb_tb
    platform = Platform(44)
    module = SimulationWrapper(platform, max_frame_length=44)
    generate_cocotb_tb(platform, module)
