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
class TbAdcPhyDac:

    def __init__(self, dut, resolution):
        self.dut = dut
        self.data_clk_period_ps = 10000

        if resolution == "10b":
            self.value_max = 2**10
        else:
            raise ValueError("Resolution {} not implemented".format(resolution))

        cocotb.fork(Clock(self.dut.rio_phy_clk, 8000).start())

        self.rtio_re = RisingEdge(self.dut.rio_phy_clk)
        self.rtio_fe = FallingEdge(self.dut.rio_phy_clk)
        self.dclk_re = RisingEdge(self.dut.data_clk)
        self.dclk_fe = FallingEdge(self.dut.data_clk)

        self.rtio_o_data = dut.data_1
        self.rtio_o_address = dut.address
        self.rtio_o_stb = dut.stb

        # cocotb.fork(self.data_generator(randomized=True))

    @cocotb.coroutine
    def write_to_rtio(self, address, data):
        yield self.rtio_fe
        self.rtio_o_address <= address
        self.rtio_o_data <= data

        self.rtio_o_stb <= 0x1
        yield self.rtio_re
        yield self.rtio_re
        self.rtio_o_stb <= 0x0

    @cocotb.coroutine
    def data_generator(self, randomized=False):
        self.dut.data_clk <= 0
        yield Timer(self.data_clk_period_ps / 2)
        while True:
            for v in range(self.value_max):
                if randomized:
                    self.dut.data <= randint(0, 1023)
                else:
                    self.dut.data <= v
                self.dut.data_clk <= 1
                yield Timer(self.data_clk_period_ps/2)
                self.dut.data_clk <= 0
                yield Timer(self.data_clk_period_ps / 2)

    @cocotb.coroutine
    def sawtooth_generator(self):
        self.dut.data_clk <= 0
        yield Timer(self.data_clk_period_ps / 2)
        while True:
            for v in range(self.value_max):
                self.dut.data <= v
                self.dut.data_clk <= 1
                yield Timer(self.data_clk_period_ps/2)
                self.dut.data_clk <= 0
                yield Timer(self.data_clk_period_ps / 2)
            for v in reversed(range(self.value_max)):
                self.dut.data <= v
                self.dut.data_clk <= 1
                yield Timer(self.data_clk_period_ps/2)
                self.dut.data_clk <= 0
                yield Timer(self.data_clk_period_ps / 2)

    @cocotb.coroutine
    def reset(self):
        print("Starting reset... ", end='')
        self.dut.dclk_rst <= 1
        self.dut.rio_phy_rst <= 1
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        self.dut.dclk_rst <= 0
        self.dut.rio_phy_rst <= 0
        print("Reset finished")

    @cocotb.coroutine
    def source_data_collector(self, pretrigger_len, posttrigger_len, event):
        pretrigger_samples = [0]*pretrigger_len
        posttrigger_samples = [0]*posttrigger_len

        while True:
            # Acqire pretrigger samples
            while self.dut.trigger_dclk != 1:
                yield self.dclk_re
                # This is basically a bad idea, but we don't expect to have A LOT of samples
                pretrigger_samples = [*pretrigger_samples[1:], self.dut.data.value.binstr]

            for i in range(posttrigger_len):
                yield self.dclk_re
                posttrigger_samples[i] = self.dut.data.value.binstr

            event.set((pretrigger_samples, posttrigger_samples))

    @cocotb.coroutine
    def readout_collector(self):
        data = []
        while self.dut.stb_1 == 0:
            yield self.rtio_re
        while self.dut.stb_1 == 1:
            data.append(self.dut.data_2.value.binstr)
            yield self.rtio_re
        return data

    @cocotb.coroutine
    def trigger_test(self, level):
        data_generator = cocotb.fork(self.sawtooth_generator())
        yield self.write_to_rtio(0x2, level)
        
        yield Timer(100, 'us')

    @cocotb.coroutine
    def parametrized_daq_test(self, pretrigger, posttrigger, iterations=1, trigger_position_coroutine=None):
        data_generator = cocotb.fork(self.data_generator(randomized=True))
        yield self.reset()

        self.dut._log.info(f"Setting pre and post trigger lengths to {pretrigger} and {posttrigger}")
        yield self.write_to_rtio(0x1, posttrigger << 12 | pretrigger)

        self.dut._log.info("Starting source data collector")
        source_data_collector_event = Event()
        source_data_collector_coroutine = cocotb.fork(self.source_data_collector(pretrigger, posttrigger, source_data_collector_event))

        yield Timer(10, 'us')  # Let source data collector fill with data

        for iteration in range(iterations):

            readout_collector = cocotb.fork(self.readout_collector())

            for _ in range(pretrigger+posttrigger):
                yield self.dclk_re

            if trigger_position_coroutine:
                yield trigger_position_coroutine

            self.dut._log.info("Triggering")
            yield self.write_to_rtio(0x0, 0x0)

            self.dut._log.info("Waiting for source data...")
            yield source_data_collector_event.wait()
            source_data = source_data_collector_event.data
            source_data_collector_event.clear()
            source_pretrigger = source_data[0]
            source_posttrigger = source_data[1]
            readout = (yield readout_collector.join())

            if len(source_pretrigger) != pretrigger:
                raise TestError(f"Invalid pretrigger data length {len(source_pretrigger)} != {pretrigger}")

            if len(source_posttrigger) != posttrigger:
                raise TestError(f"Invalid posttrigger data length {len(source_posttrigger)} != {posttrigger}")

            expected_data_len = (len(source_pretrigger) + len(source_posttrigger))
            self.dut._log.info(len(readout))
            if expected_data_len != len(readout):
                raise TestError(f"Readout length is different than source data length {expected_data_len} != {len(readout)}")

            for idx, (i, j) in enumerate(zip([*source_pretrigger, *source_posttrigger], readout)):
                if i != j:
                    raise TestError("Data different, iteration {}, at {}, {} != {}".format(iteration, idx, i, j))

            print("Iteration {} OK".format(iteration))

            # for _ in range(pretrigger+posttrigger):
            #     yield self.dclk_re

        source_data_collector_coroutine.kill()
        data_generator.kill()


@cocotb.test(skip=False)
def trigger_generator_test(dut):
    tb = TbAdcPhyDac(dut, "10b")
    yield tb.trigger_test(level=512)



@cocotb.test(skip=True)
def trigger_position_test(dut):
    tb = TbAdcPhyDac(dut, "10b")

    combinations = [
        [1, 2],
        [2, 2],
        [3, 2],
        [100, 2],
        [2000, 2],
        [1, 2000],
        [2, 2000],
        [3, 2000],
        [100, 1900],
        [100, 2],
        [2000, 2]
    ]

    for pretrigger, posttrigger in combinations:       
        yield tb.parametrized_daq_test(pretrigger, posttrigger, iterations=3)




