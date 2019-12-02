from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *

from misoc.interconnect.csr import *


class XilinxIdelayE2(Module):
    def __init__(self, data_i, data_o):
        self.delay = Signal(5)
        self.delay_ld = Signal()
        self.specials += Instance("IDELAYE2",
                                  # Parameters
                                  # p_INVCTRL_SEL="FALSE",           # Enable dynamic clock inversion (FALSE, TRUE)
                                  p_DELAY_SRC="IDATAIN",           # Delay input (IDATAIN, DATAIN)
                                  p_HIGH_PERFORMANCE_MODE="FALSE", # Reduced jitter ("TRUE"), Reduced power ("FALSE")
                                  p_IDELAY_TYPE="FIXED",           # FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
                                  p_IDELAY_VALUE=0,                # Input delay tap setting (0-31)
                                  p_PIPE_SEL="FALSE",              # Select pipelined mode, FALSE, TRUE
                                  p_REFCLK_FREQUENCY=200.0,        # IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
                                  p_SIGNAL_PATTERN="DATA",         # DATA, CLOCK input signal
                                  # Ports
                                  i_DATAIN=0,                      # 1-bit input: Internal delay data input
                                  o_DATAOUT=data_o,                # 1-bit output: Delayed data output
                                  i_C=ClockSignal(),               # 1-bit input: Clock input
                                  i_CE=0,                          # 1-bit input: Active high enable increment/decrement input
                                  i_CINVCTRL=0,  # 1-bit input: Dynamic clock inversion input
                                  i_CNTVALUEIN=self.delay,  # 5-bit input: Counter value input
                                  o_CNTVALUEOUT=Signal(),  # 5-bit output: Counter value output
                                  i_IDATAIN=data_i,  # 1-bit input: Data input from the I/O
                                  i_INC=0,  # 1-bit input: Increment / Decrement tap delay input
                                  i_LD=self.delay_ld,  # 1-bit input: Load IDELAY_VALUE input
                                  i_LDPIPEEN=0,  # 1-bit input: Enable PIPELINE register to load data input
                                  i_REGRST=ResetSignal())  # 1-bit input: Active-high reset tap-delay input


class XilinxDDRInputImplS7(Module):
    def __init__(self, i, o1, o2, clk, clk_edge="SAME_EDGE"):
        self.specials += Instance("IDDR",
                p_DDR_CLK_EDGE=clk_edge,
                i_C=clk, i_CE=1, i_S=0, i_R=0,
                i_D=i, o_Q1=o1, o_Q2=o2,
        )

class XilinxIdelayctrl(Module):
    def __init__(self, refclk):
        self.specials += Instance("IDELAYCTRL",
                i_REFCLK=refclk, i_RST=ResetSignal()
        )


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
