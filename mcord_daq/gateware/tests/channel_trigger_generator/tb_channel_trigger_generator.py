import cocotb
import random
import time

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from cocotb.utils import get_sim_time

from mcord_daq.gateware.tests.common.stream_tools import StreamMonitor, StreamDriver


max_acquisitions = 16
max_acquisition_len = 1024


class TbThrottler:

    def __init__(self, dut, seed=None):
        self.dut = dut
        self.data_width = len(dut.data_i)

        if seed is None:
            seed = time.time()
        random.seed(seed)

        cocotb.fork(Clock(self.dut.sys_clk, 8, 'ns').start())
        cocotb.fork(Clock(self.dut.dclk_i, 10, 'ns').start())

        self.re_sys = RisingEdge(self.dut.sys_clk)
        self.re_dclk = RisingEdge(self.dut.dclk_i)

        self.triggers = []
        self.data_change_ts = []

        cocotb.fork(self.monitor_triggers())

    async def reset(self):
        self.dut.dclk_rst_i <= 1
        self.dut.sys_rst <= 1
        self.dut.baseline_i <= 0
        self.dut.trigger_mode_i <= 0
        self.dut.trigger_level_i <= 0
        await self.re_sys
        await self.re_dclk
        self.dut.dclk_rst_i <= 0
        self.dut.sys_rst <= 0
        self.dut._log.info("DUT reset done.")

    async def drive_data(self, periods, level_low, level_high, length):
        data = [level_low]*(length//2) + [level_high]*(length//2)
        data = [*data]*periods
        d_prev = data[0]
        for d in data:
            await self.re_dclk
            self.dut.data_i <= d
            if d != d_prev:
                self.data_change_ts.append(get_sim_time('ns'))
            d_prev = d

    async def configure(self, mode, level, baseline):
        await self.re_sys
        self.dut.trigger_mode_i <= mode
        self.dut.trigger_level_i <= level
        self.dut.baseline_i <= baseline
        await self.re_sys

    async def monitor_triggers(self):
        while True:
            await RisingEdge(self.dut.trigger_o)
            self.triggers.append(get_sim_time('ns'))





@cocotb.test()
async def test_no_arm(dut):
    """If arm was not issued there should be no transactions"""
    tb = TbThrottler(dut)
    await tb.reset()
    await tb.configure(0b010, 0xFFFF//2, 0x0)
    await Timer(100, 'ns')
    await tb.drive_data(10, 0x0, 0xFFFF, 100)
    print(tb.triggers)
    print(tb.data_change_ts)
