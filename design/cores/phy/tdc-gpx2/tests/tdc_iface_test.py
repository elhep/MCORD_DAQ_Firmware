import random

import cocotb

from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock


def int_to_bits(i, length):
    if i < 0:
        raise ValueError("Number mus be >= 0")
    return [int(x) for x in bin(i)[2:].zfill(length)]

# noinspection PyStatementEffect
class LvdsInterfaceTb:

    def __init__(self, dut, clk_freq_mhz, delay_ps):
        self.dut = dut
        self.clk_period_ps = int(1.0/clk_freq_mhz*1e6)
        self.delay_ps = delay_ps

        self.re = RisingEdge(dut.data_clk_i)
        self.fe = FallingEdge(dut.data_clk_i)

    @cocotb.coroutine
    def initialize(self):
        self.dut.data_i <= 0
        self.dut.frame_i <= 0
        self.dut.sys_rst <= 1
        cocotb.fork(Clock(self.dut.data_clk_i, self.clk_period_ps).start())
        for _ in range(10):
            yield self.re
        self.dut.sys_rst <= 0
        for _ in range(100):
            yield self.re

    @cocotb.coroutine
    def _drive_frame(self):
        self.dut.frame_i <= 1
        yield Timer(4*self.clk_period_ps)
        self.dut.frame_i <= 0

    @cocotb.coroutine
    def _transfer_frames(self, data):
        for frame in data:
            cocotb.fork(self._drive_frame())
            for d in frame:
                self.dut.data_i <= d
                yield Timer(self.clk_period_ps/2)
            self.dut.data_i <= 0

    @cocotb.coroutine
    def send_data_frames(self, data):
        if self.delay_ps < 0:
            yield self.fe
            yield Timer(self.clk_period_ps/2+self.delay_ps)
        else:
            yield self.re
            yield Timer(self.delay_ps)
        yield self._transfer_frames(data)


@cocotb.test()
def run_tests(dut):
    tb = LvdsInterfaceTb(dut, 100, 320)
    dut.frame_length_i <= 44
    yield tb.initialize()
    frames = [
        int_to_bits(0xAAAAAAAAAAA, 44),
        int_to_bits(0xF0F0F0F0F0F, 44),
        int_to_bits(0x123456789AB, 44)
    ]
    yield tb.send_data_frames(frames)
    # yield tb.send_data_frame(int_to_bits(0xF0F0F0F0F0F, 44))
    # yield tb.send_data_frame(int_to_bits(0x123456789AB, 44))

    yield Timer(100, 'ns')