import random
import cocotb

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Join
from cocotb.clock import Clock
from gateware.simulation.cocotb_rtlink import RtLinkCSR


def int_to_bits(i, length):
    if i < 0:
        raise ValueError("Number mus be >= 0")
    return [int(x) for x in bin(i)[2:].zfill(length)]


# noinspection PyStatementEffect
class TbTdcGpx2Phy:

    def __init__(self, dut, dclk_freq_mhz, rio_phy_freq_mhz):
        self.dut = dut
        self.clk_period_ps = int(1.0 / dclk_freq_mhz * 1e6)
        self.rio_period_ps = int(1.0 / rio_phy_freq_mhz * 1e6)

        self.re = RisingEdge(dut.dclk_p)
        self.fe = FallingEdge(dut.dclk_p)

        self.channel_csr = [
            RtLinkCSR(definition_file_path="rtlinkcsr_tdc_gpx_channel_phy.txt",
                      rio_phy_clock=self.dut.rio_phy_clk,
                      stb_i=getattr(self.dut, "rtlink{}_stb_i".format(i)),
                      data_i=getattr(self.dut, "rtlink{}_data_i".format(i)),
                      address_i=getattr(self.dut, "rtlink{}_address_i".format(i)),
                      stb_o=getattr(self.dut, "rtlink{}_stb_o".format(i)),
                      data_o=getattr(self.dut, "rtlink{}_data_o".format(i)))
            for i in range(4)]

    @cocotb.coroutine
    def initialize(self):
        self.dut.sys_rst <= 1
        self.dut.rio_phy_rst <= 1

        cocotb.fork(Clock(self.dut.dclk_p, self.clk_period_ps).start(start_high=True))
        cocotb.fork(Clock(self.dut.dclk_n, self.clk_period_ps).start(start_high=False))

        cocotb.fork(Clock(self.dut.rio_phy_clk, self.rio_period_ps).start())

        for _ in range(10):
            yield self.re
        self.dut.sys_rst <= 0
        for _ in range(100):
            yield self.re
        self.dut.rio_phy_rst <= 0

    @cocotb.coroutine
    def generate_frame_signal(self, ch, frame_offset):
        frp = getattr(self.dut, "frame{}_p".format(ch))
        frn = getattr(self.dut, "frame{}_n".format(ch))
        yield self.re
        yield Timer(frame_offset)
        frp <= 1
        frn <= 0
        yield Timer(4 * self.clk_period_ps)
        frp <= 0
        frn <= 1

    @cocotb.coroutine
    def generate_data_signal(self, ch, bits, data_offset):
        dp = getattr(self.dut, "data{}_p".format(ch))
        dn = getattr(self.dut, "data{}_n".format(ch))
        yield self.re
        yield Timer(data_offset)
        for b in bits:
            dp <= b
            dn <= ~b
            yield Timer(self.clk_period_ps/2.0)
        dp <= 0
        dn <= 1

    @cocotb.coroutine
    def transfer_frame(self, ch, bits, frame_offset=0.0, data_offset=0.0):
        frame = cocotb.fork(self.generate_frame_signal(ch, frame_offset))
        data = cocotb.fork(self.generate_data_signal(ch, bits, data_offset))

        yield Combine(Join(frame), Join(data))


@cocotb.test()
def run_csr_test(dut):
    tb = TbTdcGpx2Phy(dut, 100, 125)
    yield tb.initialize()
    yield tb.channel_csr[0].frame_length.write(0x3A)
    readout = yield tb.channel_csr[0].frame_length.read()
    print(readout)

#
# @cocotb.test()
# def run_tests(dut):
#     tb = TbTdcGpx2(dut, 100, 320)
#     dut.frame_length_i <= 44
#     yield tb.initialize()
#     frames = [
#         int_to_bits(0xAAAAAAAAAAA, 44),
#         int_to_bits(0xF0F0F0F0F0F, 44),
#         int_to_bits(0x123456789AB, 44)
#     ]
#     yield tb.send_data_frames(frames)
#     yield Timer(100, 'ns')
