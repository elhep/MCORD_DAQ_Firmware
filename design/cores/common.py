from migen import *


class XilinxIdelayE2(Module):
    def __init__(self, data_i, data_o, delay_i, delay_ld_i):

        self.specials += Instance("IDELAYE2",
                                  # Parameters
                                  # p_INVCTRL_SEL="FALSE",           # Enable dynamic clock inversion (FALSE, TRUE)
                                  p_DELAY_SRC="IDATAIN",           # Delay input (IDATAIN, DATAIN)
                                  p_HIGH_PERFORMANCE_MODE="TRUE", # Reduced jitter ("TRUE"), Reduced power ("FALSE")
                                  p_IDELAY_TYPE="VAR_LOAD",           # FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
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
                                  i_CNTVALUEIN=delay_i,  # 5-bit input: Counter value input
                                  i_IDATAIN=data_i,  # 1-bit input: Data input from the I/O
                                  i_INC=0,  # 1-bit input: Increment / Decrement tap delay input
                                  i_LD=delay_ld_i,  # 1-bit input: Load IDELAY_VALUE input
                                  i_LDPIPEEN=0,  # 1-bit input: Enable PIPELINE register to load data input
                                  i_REGRST=ResetSignal(),  # 1-bit input: Active-high reset tap-delay input
        )


class XilinxDDRInputImplS7(Module):
    def __init__(self, i, o1, o2, clk, clk_edge="SAME_EDGE"):
        self.specials += Instance("IDDR",
                p_DDR_CLK_EDGE=clk_edge,
                i_C=clk, i_CE=1, i_S=0, i_R=0,
                i_D=i, o_Q1=o1, o_Q2=o2,
        )

class XilinxIdelayctrl(Module):
    def __init__(self, refclk):
        self.rdy = Signal()
        self.specials += Instance("IDELAYCTRL",
                i_REFCLK=refclk, i_RST=ResetSignal(), o_RDY=self.rdy
        )