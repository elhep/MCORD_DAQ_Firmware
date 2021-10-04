import cocotb
import random
import time

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from random import randint, seed
from itertools import product


max_acquisitions = 16
max_acquisition_len = 1024


class TbTagger:

    def __init__(self, dut):
        self.dut = dut

        cocotb.fork(Clock(self.dut.sys_clk, 8000).start())

        self.re = RisingEdge(self.dut.sys_clk)
        self.fe = FallingEdge(self.dut.sys_clk)

        self.run_data_monitor = True
        self.collected_data = []

    @cocotb.coroutine
    def enqueue_tag(self, tag):
        yield self.fe
        self.dut.tag_i <= tag
        self.dut.tag_valid_i <= 1
        yield self.fe
        self.dut.tag_i <= 0
        self.dut.tag_valid_i <= 0

    @cocotb.coroutine
    def drive_data(self, num, random=False, valid=False):
        if random:
            data = [randint(0, 2**len(self.dut.data_i)-1) for _ in range(num)]
        else:
            data = [_ % (2**len(self.dut.data_i)-1) for _ in range(num)]
        
        yield self.fe
        if valid:
            self.dut.data_valid_i <= 1
        for idx, value in enumerate(data):    
            self.dut.data_i <= value
            yield self.fe
        self.dut.data_valid_i <= 0
        return data

    @cocotb.coroutine
    def data_monitor(self):
        while self.run_data_monitor:
            yield self.re
            if bool(self.dut.data_valid_o.value):
                data_packet = []
                while self.run_data_monitor and bool(self.dut.data_valid_o.value):
                    data_packet.append(self.dut.data_o.value.integer)
                    yield self.re
                self.collected_data.append(data_packet)
            
    @cocotb.coroutine
    def reset(self):
        self.dut.tag_i <= 0
        self.dut.tag_valid_i <= 0
        self.dut.data_i <= 0
        self.dut.data_valid_i <= 0
        self.dut.sys_rst <= 1
        yield self.re
        yield self.re
        self.dut.sys_rst <= 0
        self.dut._log.info("DUT reset done.")

    @cocotb.coroutine
    def simple_run(self, seed=None):
        if seed is None:
            seed = time.time()
        random.seed(seed)

        yield self.reset()

        self.dut._log.info(f"Seed: {seed}")

        self.run_data_monitor = True
        self.collected_data = []

        dmon = cocotb.fork(self.data_monitor())
        
        yield self.enqueue_tag(0x1234)
        yield self.enqueue_tag(0x5678)
        yield self.drive_data(10, random=False, valid=False)
        yield self.drive_data(10, random=False, valid=True)
        yield self.drive_data(10, random=False, valid=False)
        yield self.drive_data(10, random=False, valid=True)

        yield Timer(100, 'ns')
             
        self.run_data_monitor = False
        yield dmon

        for collection in self.collected_data:
            print([hex(x)[2:].zfill(8) for x in collection])

        

@cocotb.test()
def test(dut):
    tb = TbTagger(dut)
    seed = 1633012016.4046054
    
    yield tb.simple_run(seed)
    