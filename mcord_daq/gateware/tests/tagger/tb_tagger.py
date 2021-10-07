import cocotb
import random
import time

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from mcord_daq.gateware.tests.common.stream_tools import StreamMonitor, StreamDriver


max_acquisitions = 16
max_acquisition_len = 1024


class TbTagger:

    def __init__(self, dut, seed=None):
        self.dut = dut

        if seed is None:
            seed = time.time()
        random.seed(seed)

        cocotb.fork(Clock(self.dut.sys_clk, 8000).start())

        self.re = RisingEdge(self.dut.sys_clk)
        self.fe = FallingEdge(self.dut.sys_clk)

        self.sink_transactions = []
        self.source_transactions = []

        self.sink_driver = StreamDriver(dut, "sink", self.dut.sys_clk, config={"scatterStb": False})
        self.sink_monitor = StreamMonitor(dut, "sink", self.dut.sys_clk, callback=self.sink_monitor_callback)
        self.source_monitor = StreamMonitor(dut, "source", self.dut.sys_clk, callback=self.source_monitor_callback)

    async def enqueue_tag(self, tag):
        await self.fe
        self.dut.tag_i <= tag
        self.dut.tag_valid_i <= 1
        await self.fe
        self.dut.tag_i <= 0
        self.dut.tag_valid_i <= 0

    async def reset(self):
        self.dut.tag_i <= 0
        self.dut.tag_valid_i <= 0
        self.dut.sink_payload_data <= 0
        self.dut.sink_stb <= 0
        self.dut.sys_rst <= 1
        await self.re
        await self.re
        self.dut.sys_rst <= 0
        self.dut._log.info("DUT reset done.")

    def sink_monitor_callback(self, data):
        self.sink_transactions.append(data)

    def source_monitor_callback(self, data):
        tag_id_width = len(self.dut.tag_i)
        value_width = len(self.dut.sink_payload_data)
        transaction = []
        for d in data:
            tag = (d >> tag_id_width)
            value = d & (2**value_width-1)
            transaction.append((tag, value))
        self.source_transactions.append(transaction)

    @staticmethod
    def random_list(num, bits=16):
        return [random.randint(0, 2 ** bits - 1) for _ in range(num)]

    async def test_data_packet(self, num, randomize=True, no_check=False, expect_tag=None):
        value_width = len(self.dut.sink_payload_data)
        source_len_pre = len(self.source_transactions)
        sink_len_pre = len(self.sink_transactions)
        data = self.random_list(num) if randomize else [x % 2**value_width for x in range(num)]
        await self.sink_driver.send(data)
        await Timer(100, "ns")
        assert sink_len_pre+1 == len(self.sink_transactions)
        if no_check:
            return
        assert source_len_pre+1 == len(self.source_transactions)
        assert len(self.sink_transactions[-1]) == len(self.source_transactions[-1])
        assert all([a == b[1] for a, b in zip(self.sink_transactions[-1], self.source_transactions[-1])])
        if expect_tag:
            tag = None
            for t in self.source_transactions[-1]:
                if tag is None:
                    tag = t[0]
                    assert tag == expect_tag
                assert t[0] == tag


@cocotb.test()
async def test_no_tag(dut):
    """Run data without enqueued any tag"""
    tb = TbTagger(dut, seed=1234)
    await tb.reset()
    await Timer(50, 'ns')
    await tb.test_data_packet(30, randomize=False, expect_tag=0xFFFF)


@cocotb.test()
async def test_run_to_invalid(dut):
    """Enqueue single tag, run data twice"""
    tb = TbTagger(dut, seed=1234)
    await tb.reset()
    await Timer(50, 'ns')
    await tb.enqueue_tag(0x1234)
    await Timer(24, 'ns')
    await tb.test_data_packet(30, randomize=False, expect_tag=0x1234)
    await tb.test_data_packet(30, randomize=False, expect_tag=0xFFFF)


@cocotb.test()
async def test_run_two_tags(dut):
    """Enqueue two tags, run data twice"""
    tb = TbTagger(dut, seed=1234)
    await tb.reset()
    await Timer(50, 'ns')
    await tb.enqueue_tag(0x1234)
    await tb.enqueue_tag(0x5678)
    await Timer(24, 'ns')
    await tb.test_data_packet(30, randomize=False, expect_tag=0x1234)
    await tb.test_data_packet(30, randomize=False, expect_tag=0x5678)


@cocotb.test()
async def test_long_run(dut):
    """Run two subsequent two tags tests"""
    tb = TbTagger(dut, seed=1234)
    await tb.reset()
    await Timer(50, 'ns')
    await tb.enqueue_tag(0x1234)
    await tb.enqueue_tag(0x5678)
    await Timer(24, 'ns')
    await tb.test_data_packet(30, randomize=False, expect_tag=0x1234)
    await tb.test_data_packet(30, randomize=False, expect_tag=0x5678)
    await tb.enqueue_tag(0x1234)
    await tb.enqueue_tag(0x5678)
    await Timer(24, 'ns')
    await tb.test_data_packet(30, randomize=False, expect_tag=0x1234)
    await tb.test_data_packet(30, randomize=False, expect_tag=0x5678)