import cocotb
import random

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock

from mcord_daq.gateware.tests.common.stream_tools import StreamMonitor, StreamDriver


max_acquisitions = 16
max_acquisition_len = 1024

seed = 1234


class TbThrottler:

    def __init__(self, dut, seed=None):
        self.dut = dut

        random.seed(seed)

        cocotb.fork(Clock(self.dut.sys_clk, 8000).start())

        self.re = RisingEdge(self.dut.sys_clk)
        self.fe = FallingEdge(self.dut.sys_clk)

        self.sink_transactions = []
        self.source_transactions = []

        self.sink_driver = StreamDriver(dut, "sink", self.dut.sys_clk, config={"scatterStb": True})
        self.sink_monitor = StreamMonitor(dut, "sink", self.dut.sys_clk, callback=self.sink_monitor_callback)
        self.source_monitor = StreamMonitor(dut, "source", self.dut.sys_clk, callback=self.source_monitor_callback)

    def sink_monitor_callback(self, data):
        self.sink_transactions.append(data)

    def source_monitor_callback(self, data):
        self.source_transactions.append(data)

    async def reset(self):
        self.dut.arm_i <= 0
        self.dut.rst_i <= 0
        self.dut.sink_stb <= 0
        self.dut.sink_eop <= 0
        self.dut.sys_rst <= 1
        await self.re
        await self.re
        self.dut.sys_rst <= 0
        self.dut._log.info("DUT reset done.")

    async def arm(self, acq_num, acq_len):
        await self.re
        self.dut.acq_num_i <= acq_num
        self.dut.acq_len_i <= acq_len
        self.dut.arm_i <= 1
        await self.re
        self.dut.arm_i <= 0

    async def reset_arm(self):
        await self.re
        self.dut.rst_i <= 1
        await self.re
        self.dut.rst_i <= 0

    async def test_data_packet(self, num, expect_source, randomize=True, no_check=False):
        source_len_pre = len(self.source_transactions)
        sink_len_pre = len(self.sink_transactions)
        data = self.random_list(num) if randomize else [x % 2**16 for x in range(num)]
        await self.sink_driver.send(data)
        await Timer(100, "ns")
        assert sink_len_pre+1 == len(self.sink_transactions)
        if no_check:
            return
        if expect_source:
            assert source_len_pre+1 == len(self.source_transactions)
            assert len(self.sink_transactions[-1]) == len(self.source_transactions[-1])
            assert all([a == b for a, b in zip(self.sink_transactions[-1], self.source_transactions[-1])])
        else:
            assert source_len_pre == len(self.source_transactions)

    @staticmethod
    def random_list(num, bits=16):
        return [random.randint(0, 2**bits-1) for _ in range(num)]


@cocotb.test()
async def test_no_arm(dut):
    """If arm was not issued there should be no transactions"""
    tb = TbThrottler(dut)
    await tb.reset()
    tb.dut.acq_num_i <= 10
    tb.dut.acq_len_i <= 10
    await tb.test_data_packet(10, False)


@cocotb.test()
async def test_prearm(dut):
    """First transaction after ARM is to be ignored to ensure a full packet acquisition"""
    tb = TbThrottler(dut)
    await tb.reset()
    await tb.arm(3, 80)
    await tb.test_data_packet(10, False)


@cocotb.test()
async def test_numer_of_transactions(dut):
    """Source should not present more than 3 transactions"""
    tb = TbThrottler(dut)
    await tb.reset()
    await tb.arm(3, 80)
    # First after arm is to be ignored
    await tb.test_data_packet(10, False)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, False)


@cocotb.test()
async def test_multi_arm(dut):
    """Source should not present more than 3 transactions"""
    tb = TbThrottler(dut)
    await tb.reset()
    await tb.arm(2, 80)
    # First after arm is to be ignored
    await tb.test_data_packet(10, False)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, False)
    await tb.test_data_packet(30, False)
    await tb.arm(2, 80)
    await tb.test_data_packet(10, False)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, True)
    await tb.test_data_packet(30, False)
    await tb.test_data_packet(30, False)


@cocotb.test()
async def test_arm_reset_between_transactions(dut):
    """Reset arm state between transactions"""
    tb = TbThrottler(dut)
    await tb.reset()
    await tb.arm(3, 80)
    # First after arm is to be ignored
    await tb.test_data_packet(10, False)
    await tb.test_data_packet(30, True)
    await tb.reset_arm()
    await tb.test_data_packet(30, False)


@cocotb.test()
async def test_arm_reset_during_transaction(dut):
    """Reset arm state"""
    tb = TbThrottler(dut)
    await tb.reset()
    await tb.arm(3, 80)
    # First after arm is to be ignored
    await tb.test_data_packet(10, False)
    source_len = len(tb.source_transactions)
    # This will take at least 30*8ns = 240 ns
    packet_sender = cocotb.fork(tb.test_data_packet(30, False, no_check=True))
    await Timer(100, 'ns')
    await tb.reset_arm()
    await packet_sender
    assert source_len == len(tb.source_transactions)


