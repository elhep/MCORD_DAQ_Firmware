import random
from itertools import product
from random import randint
from collections import namedtuple

import sys, os
sys.path.append(os.path.abspath("../../../../modules/ELHEP_Cores"))

import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Join, First
from cocotb.clock import Clock
from cocotb.result import TestFailure

import numpy as np

from elhep_cores.simulation.cocotb_rtlink import RtLinkIface


def int_to_bits(i, length):
    if i < 0:
        raise ValueError("Number mus be >= 0")
    return [int(x) for x in bin(i)[2:].zfill(length)]


class TriggerControllerTB:
    """
    Testbench assumes we're simulating 4 input channels representing 
    2 scintilators. Triggers 0 and 1 are scintilator 0, 2 and 3 
    scintilator 1. The same goes with output channels.
    """

    def __init__(self, dut, l0_num=2, l1_num=2, trig_num=4, output_num=4,
            debug=False):
        self.dut = dut
        self.fe = FallingEdge(dut.rio_phy_clk)
        self.re = RisingEdge(dut.rio_phy_clk)
        cocotb.fork(Clock(dut.rio_phy_clk, 8, 'ns').start())
        self.reset_rtlink = \
            RtLinkIface.get_iface_by_prefix(dut, "reset_phy_rtio", debug=debug)
        self.l0_rtlink = [
            RtLinkIface.get_iface_by_prefix(dut, f"l0_{i}_rtio", debug=debug) 
            for i in range(l0_num)
        ]
        self.l1_rtlink = [
            RtLinkIface.get_iface_by_prefix(dut, f"l1_{i}_rtio", debug=debug) 
            for i in range(l1_num)
        ]
        self.output_config_rtlink = \
            RtLinkIface.get_iface_by_prefix(dut, f"output_config_rtio", 
                debug=debug) 
        self.trigger = [
            getattr(dut, f"trigger_in_{idx}") for idx in range(trig_num)
        ]
        self.output = [
            getattr(dut, f"trigger_out_{idx}") for idx in range(output_num)
        ]
        self.output_id = [
            getattr(dut, f"trigger_out_id_{idx}") for idx in range(output_num)
        ]

    async def reset(self):
        await self.set_triggers(0x0)
        await self.set_reset(1)
        await Timer(30, 'ns')
        await self.set_reset(0)
        await Timer(300, 'ns')

    async def set_reset(self, state):
        await self.reset_rtlink.write(state)

    async def configure_layer(self, target, idx, pulse_length, mask):
        await target[idx].write(pulse_length, 0x1 << 1 | 1)
        await target[idx].write(mask, 0x2 << 1 | 1)

    async def enable_layer(self, target, idx, enabled=True):
        await target[idx].write(int(enabled), 0x0 << 1 | 1)

    async def configure_output(self, idx, mask):
        await self.output_config_rtlink.write(mask, idx << 1 | 1)

    async def set_triggers(self, mask):
        await self.fe
        for idx, trigger in enumerate(self.trigger):
            trigger <= (mask >> idx) & 0x1
        await self.re
    
    async def pulse_trigger(self, idx):
        await self.fe
        self.trigger[idx] <= 1
        await self.re
        await self.fe
        self.trigger[idx] <= 0


async def run_for_ax(tb, trigger_delay, enable):
    await tb.reset()

    # Scintilator 0 - inputs
    await tb.configure_layer(tb.l0_rtlink, 0, 10, 0b0011)
    # Scintilator 1 - inputs
    await tb.configure_layer(tb.l0_rtlink, 1, 10, 0b1100)
    
    # Configure coincidence - detecting single board events
    await tb.configure_layer(tb.l1_rtlink, 0, 10, 0b01) 
    await tb.configure_layer(tb.l1_rtlink, 1, 10, 0b10)

    # Scintilator 0 outputs from L1/0
    await tb.configure_output(0, 0b01)
    await tb.configure_output(1, 0b01)

    # Scintilator 1 outputs from L1/1
    await tb.configure_output(2, 0b10)
    await tb.configure_output(3, 0b10)

    # Enable all layers
    if enable:
        for target, idx in product([tb.l0_rtlink, tb.l1_rtlink], range(2)):
            await tb.enable_layer(target, idx)

    pattern_finished = False
    async def trigger_pattern():
        nonlocal pattern_finished
        for i in range(100):
            await tb.pulse_trigger(i % 4)
            await Timer(trigger_delay, 'ns')
        await Timer(400, 'ns')
        pattern_finished = True
    
    trigger_counter = [0] * 4
    trigger_ids = [[] for _ in range(4)]
    async def count_triggers():
        while not pattern_finished:
            await tb.re
            for i in range(4):
                if tb.output[i].value.is_resolvable:
                    if tb.output[i] == 1:
                        trigger_counter[i] += 1
                        value = tb.output_id[i].value.integer
                        trigger_ids[i].append({
                            "id": value & 0x1,
                            "cnt": value >> 1
                        })
    
    cocotb.fork(trigger_pattern())
    await cocotb.fork(count_triggers())

    return trigger_counter, trigger_ids


def check_cnt(values):
    for i in range(1, len(values)):
        diff = values[i]-values[i-1]
        if diff not in [1, -15]:
            raise TestFailure(f"Invalid cnt ({diff})")


@cocotb.test()
async def test_A0(dut):
    """Pulses on every channel with a specified separatation 
    small enought so coincidence is detected but coincidence modules
    disabled."""

    tb = TriggerControllerTB(dut)

    trigger_counter, trigger_ids = await run_for_ax(tb, 70, False)
    assert sum(trigger_counter) == 0

    
@cocotb.test()
async def test_A1(dut):
    """Pulses on every channel with a specified separatation 
    large enought so coincidence is not detected, coincidence modules
    enabled."""

    tb = TriggerControllerTB(dut)

    trigger_counter, trigger_ids = await run_for_ax(tb, 100, True)
    assert sum(trigger_counter) == 0


@cocotb.test()
async def test_A2(dut):
    """Pulses on every channel with a specified separatation 
    small enought so coincidence is detected, coincidence modules
    enabled."""

    tb = TriggerControllerTB(dut)

    trigger_counter, trigger_ids = await run_for_ax(tb, 70, True)
    for tc in trigger_counter:
        assert tc == 25
    
    for ch_idx, ch_ids in enumerate(trigger_ids):
        if ch_idx in [0,1]:
            for c in ch_ids:
                assert c["id"] == 0
        elif ch_idx in [2,3]:
            for c in ch_ids:
                assert c["id"] == 1
        else:
            raise TestFailure("Invalid id")
        check_cnt([c['cnt'] for c in ch_ids])
        
