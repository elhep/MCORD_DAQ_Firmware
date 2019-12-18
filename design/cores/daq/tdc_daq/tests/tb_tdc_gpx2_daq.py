import cocotb

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from random import randint
from itertools import product


def int_to_bits(i, length):
    if i < 0:
        raise ValueError("Number mus be >= 0")
    return [int(x) for x in bin(i)[2:].zfill(length)]

# noinspection PyStatementEffect
class TbTdcGpx2Daq:

    def __init__(self, dut):
        self.dut = dut

        cocotb.fork(Clock(self.dut.rio_phy_clk, 8000).start())
        cocotb.fork(Clock(self.dut.data_clock_clk, 10000).start())

        self.rtio_re = RisingEdge(self.dut.rio_phy_clk)
        self.rtio_fe = FallingEdge(self.dut.rio_phy_clk)
        self.dclk_re = RisingEdge(self.dut.data_clock_clk)
        self.dclk_fe = FallingEdge(self.dut.data_clock_clk)

        self.rtlink = {
            "main": {
                "clock": self.dut.rio_phy_clk,
                "input": {
                    "stb": dut.rtlink_stb_o,
                    "data": dut.rtlink_data_o},
                 "output": {
                     "stb": dut.rtlink_stb_i,
                     "data": dut.rtlink_data_i}
            },
            "aux": {
                "clock": self.dut.rio_phy_clk,
                "input": {
                    "stb": dut.rtlink_aux_stb_o,
                    "data": dut.rtlink_aux_data_o},
            }
        }

        self.generated_data = []
        self.collected_data = []
        self.collected_data_aux = []

    @cocotb.coroutine
    def write_rtlink(self, channel, address, data):
        link_clock = self.rtlink[channel]["clock"]

        link_addr = self.rtlink[channel].get("addr", None)
        link_data = self.rtlink[channel]["output"]["data"]
        link_stb  = self.rtlink[channel]["output"]["stb"]

        yield FallingEdge(link_clock)

        if link_addr:
            link_addr <= address
        if link_data:
            link_data <= data

        link_stb <= 0x1
        yield FallingEdge(link_clock)
        link_stb <= 0x0

    @cocotb.coroutine
    def read_rtlink(self, channel, callback):
        link_clock = self.rtlink[channel]["clock"]

        link_data = self.rtlink[channel]["input"]["data"]
        link_stb = self.rtlink[channel]["input"]["stb"]

        while True:
            yield RisingEdge(link_clock)
            if link_stb == 1:
                callback(link_data.value.binstr)

    def data_sink(self, target):
        def data_sink_wrapped(data):
            target.append(int(data, 2))
        return data_sink_wrapped

    @cocotb.coroutine
    def reset(self):
        self.dut.data_i <= 0
        self.dut.data_stb_i <= 0
        self.dut.data_clock_rst <= 0
        self.dut.rio_phy_rst <= 0

        self.dut._log.info("Waiting initial 120 ns")
        yield Timer(120, 'ns')
        self.dut._log.info("Starting reset... ")
        self.dut.data_clock_rst <= 1
        self.dut.rio_phy_rst <= 1
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        self.dut.data_clock_rst <= 0
        self.dut.rio_phy_rst <= 0
        self.dut._log.info("Reset finished")

    @cocotb.coroutine
    def data_generator(self, separation=0, randomized=False, n=None):
        def dgen():
            max=2**len(self.dut.data_i)
            while True:
                for i in range(max):
                    yield i if not randomized else randint(0, max)

        data_gen = dgen()

        @cocotb.coroutine
        def process():
            yield self.dclk_fe
            d = next(data_gen)
            if self.dut.daq_enabled_dclk == 1:
                self.generated_data.append(d)
            self.dut.data_i <= d
            self.dut.data_stb_i <= 1
            for _ in range(separation):
                yield self.dclk_fe
                self.dut.data_stb_i <= 0

        if n is None:
            while True:
                yield process()
        else:
            for _ in range(n):
                yield process()

        if separation == 0:
            self.dut.data_stb_i <= 0

    def validate_data(self):
        if len(self.generated_data) != len(self.collected_data) != len(self.collected_data_aux):
            raise TestError("Generated data length != collected data length")

        for idx, (g, c, caux) in enumerate(zip(self.generated_data, self.collected_data, self.collected_data_aux)):
            readout = (caux << 32) | c
            if g != readout:
                raise TestError("{}: {:11X} != {:11X} [{:8X}  {:3X}]".format(idx, g, readout, c, caux))

    @cocotb.coroutine
    def run_for_separation(self, separation):
        self.dut._log.info("Running test for separation {}".format(separation))

        yield self.reset()
        yield Timer(100, 'ns')
        collector = cocotb.fork(self.read_rtlink("main", self.data_sink(self.collected_data)))
        collector_aux = cocotb.fork(self.read_rtlink("aux", self.data_sink(self.collected_data_aux)))
        yield self.write_rtlink("main", 0, 1)
        yield Timer(50, 'ns')
        yield self.data_generator(separation=separation, n=100, randomized=False)
        yield self.write_rtlink("main", 0, 0)
        yield Timer(50, 'ns')
        yield self.data_generator(separation=separation, n=10, randomized=False)

        self.validate_data()

        collector.kill()
        collector_aux.kill()

        self.collected_data = []
        self.collected_data_aux = []
        self.generated_data = []


@cocotb.test()
def test(dut):
    tb = TbTdcGpx2Daq(dut)

    for s in [0, 1, 100]:
        yield tb.run_for_separation(s)

    

# @cocotb.test()
# def consecutive_operations_test(dut):



