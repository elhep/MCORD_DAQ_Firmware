import cocotb
import random
import time

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from random import randint, seed
from itertools import product


depth = 128


class TbCircularBuffer:

    def __init__(self, dut):
        self.dut = dut

        cocotb.fork(Clock(self.dut.sys_clk, 8000).start())

        self.re = RisingEdge(self.dut.sys_clk)
        self.fe = FallingEdge(self.dut.sys_clk)

        self.run_data_monitor = True
        self.collected_data = []

    @cocotb.coroutine
    def data_driver(self, data, trigger_at):
        for idx, d in enumerate(data):
            yield self.fe
            self.dut.data_i <= d
            if idx == trigger_at:
                self.dut.trigger_i <= 1
            else:
                self.dut.trigger_i <= 0

    @cocotb.coroutine
    def data_monitor(self):
        while self.run_data_monitor:
            yield self.re
            if bool(self.dut.source_stb.value):
                self.collected_data.append(self.dut.source_payload_data.value.integer)

    @cocotb.coroutine
    def reset(self):
        self.dut.sys_rst <= 1
        yield self.re
        yield self.re
        self.dut.sys_rst <= 0
        self.dut._log.info("DUT reset done.")

    @cocotb.coroutine
    def simple_run(self, pretrigger, posttrigger, num, seed=None):
        if seed is None:
            seed = time.time()
        random.seed(seed)

        yield self.reset()

        for _ in range(num):
            sequence_length = max((pretrigger+posttrigger)*5, 2*depth)
            trigger_at = randint(pretrigger+10, sequence_length-posttrigger-pretrigger-10)
            data = [randint(0, 2**16-1) for _ in range(sequence_length)]
            data = list(range(sequence_length))
            expected_data = data[(trigger_at-pretrigger):(trigger_at+posttrigger+1)]
            assert len(expected_data) == pretrigger+posttrigger+1

            self.dut._log.info(f"Seed: {seed}, pretrigger: {pretrigger}, posttrigger: {posttrigger}, trigger at: {trigger_at}")

            self.run_data_monitor = True
            self.collected_data = []

            self.dut.pretrigger_i <= pretrigger
            self.dut.posttrigger_i <= posttrigger

            dgen = cocotb.fork(self.data_driver(data, trigger_at))
            dmon = cocotb.fork(self.data_monitor())
            
            yield dgen

            self.run_data_monitor = False
            yield dmon

            assert len(expected_data) == len(self.collected_data)
            for idx, (expected, collected) in enumerate(zip(expected_data, self.collected_data)):
                assert expected == collected, f"Invalid data at position {idx}, seed {seed}"
        

@cocotb.test()
def test(dut):
    tb = TbCircularBuffer(dut)
    seed = None
    # Ensure corner cases
    yield tb.simple_run(0, 0, 5, seed)
    yield tb.simple_run(0, 127, 5, seed)
    yield tb.simple_run(126, 0, 5, seed)
    yield tb.simple_run(126, 1, 5, seed)
    
    for _ in range(20):
        num = randint(1, 5)
        pretrigger = randint(0, int(depth*0.8))
        posttrigger = randint(0, depth-pretrigger-1)
        yield tb.simple_run(pretrigger, posttrigger, num, seed)
    