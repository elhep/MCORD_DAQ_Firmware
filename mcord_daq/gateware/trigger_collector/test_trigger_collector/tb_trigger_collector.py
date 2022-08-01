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


class TriggerCollectorTB:
    """
    Testbench assumes we are simulating 2 input RTIO channels, where data comes
    in form of packets.
    """

    def __init__(self, dut, trig_num=2, output_num=1,
            debug=False):
        self.dut = dut
        self.fe = FallingEdge(dut.rio_phy_clk)
        self.re = RisingEdge(dut.rio_phy_clk)
        cocotb.fork(Clock(dut.rio_phy_clk, 8, 'ns').start())
        self.reset_rtlink = \
            RtLinkIface.get_iface_by_prefix(dut, "reset_phy_rtio", debug=debug)

        self.config_rtlink = \
            RtLinkIface.get_iface_by_prefix(dut, f"config_rtio", 
                debug=debug) 

        self.rtlink_packet_input = []
        for i in range(trig_num):
            self.rtlink_packet_input += [RtLinkIface.get_iface_by_prefix(dut, f"input_rtio_{i}", 
                debug=debug) ]
            
        self.output = [
            getattr(dut, f"trigger")
        ]

    async def reset(self):
        await self.set_reset(1)
        await Timer(30, 'ns')
        await self.set_reset(0)
        await Timer(300, 'ns')

    async def set_reset(self, state):
        await self.reset_rtlink.write(state)

    # async def configure_layer(self, target, idx, pulse_length, mask):
    #     await target[idx].write(pulse_length, 0x1 << 1 | 1)
    #     await target[idx].write(mask, 0x2 << 1 | 1)

    async def enable(self):
        await self.config_rtlink.write(1, 0x0 << 1 | 1)
        await self.fe
        # await self.config_rtlink.read()
        await self.fe

    async def configure_Tmax(self, Tmax):
        await self.config_rtlink.write(Tmax, 0x1 << 1 | 1)
        await self.fe

    
    async def write_packet(self, group, ID, SystemTime):
        SyncValue = 0x1ACFFC1D
        await self.fe
        await self.rtlink_packet_input[group].write(ID<<22|SyncValue>>10)
        await self.rtlink_packet_input[group].write(SystemTime&0xFFFFFFFF)
        await self.rtlink_packet_input[group].write(SystemTime>>32)
        await self.fe

async def run_for_ax(tb): #, trigger_delay, enable):
    await tb.reset()

    # Configure Tmax to 50
    await tb.configure_Tmax(50)

    # Enable 
    await tb.enable()
    await Timer(300, 'ns')

    # Write 1st packet
    await tb.write_packet(1, 15, 1000)    

    # Write 2nd packet
    await tb.write_packet(0, 18, 1049)   
    test = False
    # Check for trigger 
    while not test:
        await tb.re
        if tb.output[0] == 1:
            test = True
    await tb.re

    # Write 1st packet
    await tb.write_packet(1, 11, 6500)    

    # Write 2nd packet
    await tb.write_packet(0, 3, 6530)   
    # Check for trigger 
    while not test:
        await tb.re
        if tb.output[0] == 1:
            test = True
    await tb.re


    await Timer(300, 'ns')


    # pattern_finished = False
    # async def trigger_pattern():
    #     nonlocal pattern_finished
    #     for i in range(100):
    #         await tb.pulse_trigger(i % 4)
    #         await Timer(trigger_delay, 'ns')
    #     await Timer(400, 'ns')
    #     pattern_finished = True
    
    # trigger_counter = [0] * 4
    # trigger_ids = [[] for _ in range(4)]
    # async def count_triggers():
    #     while not pattern_finished:
    #         await tb.re
    #         for i in range(4):
    #             if tb.output[i].value.is_resolvable:
    #                 if tb.output[i] == 1:
    #                     trigger_counter[i] += 1
    #                     value = tb.output_id[i].value.integer
    #                     trigger_ids[i].append({
    #                         "id": value & 0x1,
    #                         "cnt": value >> 1
    #                     })
    
    # cocotb.fork(trigger_pattern())
    # await cocotb.fork(count_triggers())

    # return trigger_counter, trigger_ids


# def check_cnt(values):
#     for i in range(1, len(values)):
#         diff = values[i]-values[i-1]
#         if diff not in [1, -15]:
#             raise TestFailure(f"Invalid cnt ({diff})")


@cocotb.test()
async def test_A0(dut):
    """CHANGE! Pulses on every channel with a specified separatation 
    small enought so coincidence is detected but coincidence modules
    disabled."""

    tb = TriggerCollectorTB(dut)

    await run_for_ax(tb)
    # trigger_counter, trigger_ids = await run_for_ax(tb, 70, False)
    # assert sum(trigger_counter) == 0

    
# @cocotb.test()
# async def test_A1(dut):
#     """Pulses on every channel with a specified separatation 
#     large enought so coincidence is not detected, coincidence modules
#     enabled."""

#     tb = TriggerControllerTB(dut)

#     trigger_counter, trigger_ids = await run_for_ax(tb, 100, True)
#     assert sum(trigger_counter) == 0


# @cocotb.test()
# async def test_A2(dut):
#     """Pulses on every channel with a specified separatation 
#     small enought so coincidence is detected, coincidence modules
#     enabled."""

#     tb = TriggerControllerTB(dut)

#     trigger_counter, trigger_ids = await run_for_ax(tb, 70, True)
#     for tc in trigger_counter:
#         assert tc == 25
    
#     for ch_idx, ch_ids in enumerate(trigger_ids):
#         if ch_idx in [0,1]:
#             for c in ch_ids:
#                 assert c["id"] == 0
#         elif ch_idx in [2,3]:
#             for c in ch_ids:
#                 assert c["id"] == 1
#         else:
#             raise TestFailure("Invalid id")
#         check_cnt([c['cnt'] for c in ch_ids])
        
