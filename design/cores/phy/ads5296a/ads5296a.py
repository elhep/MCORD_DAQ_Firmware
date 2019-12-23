from migen import *
from migen.build.generic_platform import *
from migen.genlib.io import DifferentialInput
from migen.genlib.resetsync import AsyncResetSynchronizer

from design.cores.common import XilinxIdelayE2



class ADS5296A_XS7(Module):

    def __init__(self, platform, adclk_i, lclk_i, dat_i):

        DAT_O_LEN = 10
        BUFR_DIVIDE = 5
        VALID_FRAME_OUT = 0b1111100000

        # Outputs
        self.data_clk_o = Signal()
        self.bitslip_done = Signal()
        self.data_o = [Signal(DAT_O_LEN, name="data_{}_o".format(i)) for i in range(9)]

        input_lines = [*dat_i, adclk_i]
        lines_delayed = [Signal(name="line_delayed_{}".format(i)) for i in range(9)]
        for idx, (input_line, line_delayed) in enumerate(zip(input_lines, lines_delayed)):
            line_buffer = Signal()
            self.specials += DifferentialInput(i_p=input_line.p,
                                               i_n=input_line.n,
                                               o=line_buffer)
            self.submodules += XilinxIdelayE2(data_i=line_buffer, data_o=line_delayed)

        # Clocking
        lclk_ibuf = Signal()
        lclk_bufio = Signal()

        self.clock_domains.cd_adclk_clkdiv = cd_div4 = ClockDomain()
        self.specials += [AsyncResetSynchronizer(cd_div4, ResetSignal("sys"))]
        platform.add_period_constraint(cd_div4.clk, 10.)

        self.specials += DifferentialInput(i_p=lclk_i.p,
                                           i_n=lclk_i.n,
                                           o=lclk_ibuf)
        self.specials += Instance("BUFIO",
                                  i_I=lclk_ibuf,
                                  o_O=lclk_bufio)
        self.specials += Instance("BUFR",
                                  p_BUFR_DIVIDE=str(BUFR_DIVIDE),
                                  i_I=lclk_ibuf,
                                  i_CE=1,
                                  i_CLR=0,
                                  o_O=cd_div4.clk)

        # Bitslip logic
        bitslip = Signal()
        bitslip_cnt = Signal(4)

        self.sync.adclk_clkdiv += [
            bitslip.eq(0),
            bitslip_cnt.eq(bitslip_cnt + 1),
            self.bitslip_done.eq(self.data_o[8] == VALID_FRAME_OUT),
            If(bitslip_cnt == 0x0,
               If(~self.bitslip_done,
                  bitslip.eq(1))),
        ]

        # ISERDES
        # For 10b deserialization we'll be using two ISERDES modules connected in MASTER-SLAVE mode.

        # In this mode stb_o is just div4 clock
        self.specials += Instance("BUFG", i_I=cd_div4.clk, o_O=self.data_clk_o)

        for idx, (line_delayed, dat_o) in enumerate(zip(lines_delayed, self.data_o)):
            shift1 = Signal(name="shift1_{}".format(idx))
            shift2 = Signal(name="shift2_{}".format(idx))
            self.specials += Instance("ISERDESE2",
                                      p_DATA_RATE="DDR",
                                      p_DATA_WIDTH=10,
                                      p_INTERFACE_TYPE="NETWORKING",
                                      p_NUM_CE=1,
                                      p_SERDES_MODE="MASTER",
                                      p_IOBDELAY="BOTH",
                                      o_Q1=dat_o[0], o_Q2=dat_o[1], o_Q3=dat_o[2], o_Q4=dat_o[3],
                                      o_Q5=dat_o[4], o_Q6=dat_o[5], o_Q7=dat_o[6], o_Q8=dat_o[7],
                                      o_SHIFTOUT1=shift1,
                                      o_SHIFTOUT2=shift2,
                                      o_O=Signal(name="output_test_master_{}".format(idx)),
                                      i_DDLY=line_delayed,
                                      i_CLK=lclk_bufio,
                                      i_CLKB=~lclk_bufio,
                                      i_CE1=1,
                                      i_RST=ResetSignal("adclk_clkdiv"),
                                      i_CLKDIV=ClockSignal("adclk_clkdiv"),
                                      i_CLKDIVP=0,
                                      i_BITSLIP=bitslip,
                                      i_DYNCLKDIVSEL=0,
                                      i_DYNCLKSEL=0)
            self.specials += Instance("ISERDESE2",
                                      p_DATA_RATE="DDR",
                                      p_DATA_WIDTH=10,
                                      p_INTERFACE_TYPE="NETWORKING",
                                      p_NUM_CE=1,
                                      p_SERDES_MODE="SLAVE",
                                      p_IOBDELAY="BOTH",
                                      o_Q3=dat_o[8], o_Q4=dat_o[9],
                                      i_SHIFTIN1=shift1,
                                      i_SHIFTIN2=shift2,
                                      i_CLK=lclk_bufio,
                                      i_CLKB=~lclk_bufio,
                                      i_CE1=1,
                                      i_RST=ResetSignal("adclk_clkdiv"),
                                      i_CLKDIV=ClockSignal("adclk_clkdiv"),
                                      i_CLKDIVP=0,
                                      i_BITSLIP=bitslip,
                                      i_DYNCLKDIVSEL=0,
                                      i_DYNCLKSEL=0)


class SimulationWrapper(Module):

    def __init__(self):

        def add_diff_signal(name):
            setattr(self, name, Signal(name=name))
            sig = getattr(self, name)
            setattr(sig, "p", Signal(name=name+"_p"))
            setattr(sig, "n", Signal(name=name+"_n"))
            return [getattr(sig, "p"), getattr(sig, "n")]

        self.io = []
        self.io += add_diff_signal("adclk_i")
        self.io += add_diff_signal("lclk_i")
        dat_i = []
        for i in range(8):
            self.io += add_diff_signal("dat_{}_i".format(i))
            dat_i.append(getattr(self, "dat_{}_i".format(i)))

        self.clock_domains.sys = cd_sys = ClockDomain()
        self.io.append(cd_sys.clk)
        self.io.append(cd_sys.rst)

        self.submodules.dut = dut = ADS5296A_XS7(self.adclk_i, self.lclk_i, dat_i)

        for i in range(9):
            self.io.append(dut.idelay_val_i[i])
        self.io.append(dut.idelay_ld_i)
        self.io.append(dut.data_clk_o)
        for i in range(8):
            self.io.append(dut.data_o[i])
        self.io.append(dut.rst_i)
        self.io.append(dut.ref_clk_200M)
        self.io.append(dut.bitslip_done)

        self.io = {*self.io}


if __name__ == "__main__":

    from migen.build.xilinx import common
    from design.simulation.common import update_tb

    module = SimulationWrapper()
    so = dict(common.xilinx_special_overrides)
    so.update(common.xilinx_s7_special_overrides)

    verilog.convert(fi=module,
                    name="top",
                    special_overrides=so,
                    ios=module.io,
                    create_clock_domains=False).write('design/cores/phy/ads5296a/tests/ADS5296A_XS7.v')
    # update_tb('design/cores/tests/adc_phy_daq/adc_phy_daq.v')









