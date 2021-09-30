import cocotb
import random
import time

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from random import randint, seed
from itertools import product


max_acquisitions = 16
max_acquisition_len = 1024


class TbThrottler:

    def __init__(self, dut):
        self.dut = dut

        cocotb.fork(Clock(self.dut.sys_clk, 8000).start())

        self.re = RisingEdge(self.dut.sys_clk)
        self.fe = FallingEdge(self.dut.sys_clk)

        self.run_data_monitor = True
        self.collected_data = []

    @cocotb.coroutine
    def data_driver(self, data):
        for data_vals, data_valid_at, data_valid_len in data:
            self.dut._log.info(f"data_valid_at: {data_valid_at}, data_valid_len: {data_valid_len}")
            for idx, d in enumerate(data_vals):
                yield self.fe
                self.dut.data_i <= d
                if data_valid_at <= idx <= data_valid_at+data_valid_len:
                    self.dut.data_valid_i <= 1
                else:
                    self.dut.data_valid_i <= 0

    @cocotb.coroutine
    def data_monitor(self):
        print(self.run_data_monitor)
        while self.run_data_monitor:
            yield self.re
            if bool(self.dut.data_valid_o.value):
                self.collected_data.append(self.dut.data_o.value.integer)

    @cocotb.coroutine
    def reset(self):
        self.dut.arm_i <= 0
        self.dut.rst_i <= 0
        self.dut.data_valid_i <= 0
        self.dut.sys_rst <= 1
        yield self.re
        yield self.re
        self.dut.sys_rst <= 0
        self.dut._log.info("DUT reset done.")

    @cocotb.coroutine
    def simple_run(self, acq_num, acq_len, seed=None):
        if seed is None:
            seed = time.time()
        random.seed(seed)

        yield self.reset()

        def get_data_sequence():
            sequence_length = int(2.5*acq_len)
            data_valid_at = randint(0, acq_len)
            data_valid_len = randint(0, 2*acq_len)
            data = [randint(0, 2**16-1) for _ in range(sequence_length)]
            # data = [_ for _ in range(sequence_length)]
            expected_upper = min(data_valid_at+acq_len, data_valid_at+data_valid_len)+1
            expected_data = data[data_valid_at:expected_upper]
            return (data, data_valid_at, data_valid_len), expected_data

        sequences_num = randint(1, 2*acq_num)
        drive_data = []
        expected_data = []
        self.dut._log.info(f"Sequences num: {sequences_num}")
        for idx in range(sequences_num):
            sq_drive_data, sq_expected_data = get_data_sequence()
            drive_data.append(sq_drive_data)
            if idx < acq_num:
                expected_data += sq_expected_data
        
        self.dut.acq_num_i <= acq_num
        self.dut.acq_len_i <= acq_len

        yield self.re
        yield self.re
        yield self.re
        
        yield self.fe
        self.dut.arm_i <= 1
        yield self.fe
        self.dut.arm_i <= 0

        self.dut._log.info(f"Seed: {seed}, acq_num: {acq_num}, acq_len: {acq_len}")

        self.run_data_monitor = True
        self.collected_data = []

        dgen = cocotb.fork(self.data_driver(drive_data))
        dmon = cocotb.fork(self.data_monitor())
        
        yield dgen
        for _ in range(100):
            yield self.re

        self.run_data_monitor = False
        yield dmon

        # for idx, (c, e) in enumerate(zip(self.collected_data, expected_data)):
        #     print(idx, c, e)

        assert len(expected_data) == len(self.collected_data), f"{len(expected_data)}, {len(self.collected_data)}"
        for idx, (expected, collected) in enumerate(zip(expected_data, self.collected_data)):
            assert expected == collected, f"Invalid data at position {idx}, seed {seed}"
        

@cocotb.test()
def test(dut):
    tb = TbThrottler(dut)
    seed = 1633012016.4046054
    
    for _ in range(100):
        acq_num = randint(1, 10)
        acq_len = randint(1, 1024)
        yield tb.simple_run(acq_num, acq_len, seed)
    