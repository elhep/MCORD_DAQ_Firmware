from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *

from migen import *
from migen.fhdl.specials import Memory
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer
from migen.fhdl import verilog
from artiq.gateware.rtio import rtlink

from functools import reduce
from operator import and_, add

from math import cos, sin, pi
from scipy import signal


class Baseline(Module):
    def __init__(self, wsize=16):

        # Defines - values are way off....
        fs = 100000000.0 # Sample
        cutoff = 10000.0  # Desired cutoff frequency, Hz
        trans_width = 10000  # Width of transition from pass band to stop band, Hz
        numtaps = 266  # Size of the FIR filter.

        # Compute filter coefficients with SciPy
        coef = signal.remez(numtaps, [0, cutoff, cutoff + trans_width, 0.5 * fs], [1, 0], Hz=fs)

        self.coef = coef
        self.wsize = wsize
        self.i = Signal((self.wsize, True))
        self.o = Signal((self.wsize, True))

        ###

        muls = []
        src = self.i
        for c in self.coef:
            sreg = Signal((self.wsize, True))
            self.sync += sreg.eq(src)
            src = sreg
            c_fp = int(c * 2 ** (self.wsize - 1))
            muls.append(c_fp * sreg)
        sum_full = Signal((2 * self.wsize - 1, True))
        self.sync += sum_full.eq(reduce(add, muls))
        self.comb += self.o.eq(sum_full >> self.wsize - 1)

        


class SimulationWrapper(Module):

    def __init__(self):
        self.data_clk = Signal()
        self.data = Signal(10)

        trigger_ext = Signal()

        self.clock_domains.cd_rio_phy = cd_rio_phy = ClockDomain()
        self.clock_domains.cd_dclk = cd_dclk = ClockDomain()

        self.comb += [cd_dclk.clk.eq(self.data_clk)]

        self.submodules.dut = dut = AdcPhyDaq(self.data_clk, self.data, 2048)

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