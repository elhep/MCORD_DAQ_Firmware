from functools import reduce
from operator import or_, and_
import json

from migen import *
from migen.fhdl import *
from migen.fhdl.specials import Memory

from migen.genlib.coding import PriorityEncoder
from migen.genlib.io import DifferentialInput
from migen.fhdl import verilog

from artiq.gateware.rtio import rtlink
from artiq.gateware.rtio.channel import Channel
from artiq.gateware.rtio.phy.ttl_simple import Output

from elhep_cores.cores.trigger_generators import TriggerGenerator, \
    RtioCoincidenceTriggerGenerator, RtioTriggerGenerator
from elhep_cores.cores.rtlink_csr import RtLinkCSR
from elhep_cores.helpers.ddb_manager import HasDdbManager
from elhep_cores.simulation.common import update_tb
from elhep_cores.cores.xilinx_ila import ILAProbe

class TriggerController(Module, HasDdbManager):

    def _add_l1_output(self, channel_trigger, identifier):
        """Adds output for single L1 channel.

        Output consists of trigger line and trigger counter + sw trigger
        """

        # Software trigger
        sw_trig_module = RtioTriggerGenerator(f"{identifier}_sw_trig")
        self.submodules += sw_trig_module
        self.add_rtio_channels(
            channel=Channel.from_phy(sw_trig_module),
            device_id=f"{identifier}_sw_trig",
            module="artiq.coredevice.ttl",
            class_name="TTLOut")

        # Coincidence OR SW trigger
        # We want only 1-period pulses on trigger rising edge here
        trigger_or = Signal()
        trigger_or_prev = Signal()
        trigger = Signal()
        self.comb += trigger_or.eq(sw_trig_module.trigger | channel_trigger)
        self.sync.rio_phy += [
            trigger_or_prev.eq(trigger_or),
            If(self.trigger_controller_reset, trigger.eq(0))
            .Else(trigger.eq(trigger_or & ~trigger_or_prev))
        ]

        # Trigger counter
        trigger_counter = Signal(self.trigger_counter_len, reset=0)
        self.sync.rio_phy += [
            If(self.trigger_controller_reset, trigger_counter.eq(0)).
            Elif(trigger, trigger_counter.eq(trigger_counter+1))
        ]

        return trigger, trigger_counter

    def __init__(self, l0_trigger_generators,  outputs, l0_num=16, l1_num=16, 
            l1_extra=[], trigger_counter_len=4, 
            module_identifier="trigger_controller", with_ila=False):
        self.module_identifier = module_identifier
        self.trigger_counter_len = trigger_counter_len
        self.trigger_id_len = len(Signal(max=max(l1_num, 2)))

        assert self.trigger_id_len + trigger_counter_len <= 8

        # Trigger counter reset 
        self.trigger_controller_reset = Signal()
        phy = Output(self.trigger_controller_reset)
        self.submodules.reset_phy = phy
        self.add_rtio_channels(
                channel=Channel.from_phy(phy),
                device_id=f"{module_identifier}_trigger_controller_reset",
                module="artiq.coredevice.ttl",
                class_name="TTLOut")

        # Output config CSR
        l1_extra_triggers_num = sum([len(m.triggers) for m in l1_extra])
        l1_total_num = l1_num+l1_extra_triggers_num
        # FIXME: Add support for long RTIO output
        assert l1_total_num <= 32
        regs = [
            ("{}_l1_mask".format(output['label']), l1_total_num)
            for output in outputs
        ]
        output_config_phy = RtLinkCSR(regs, "output_config", 
            f"{module_identifier}_output_config")
        self.submodules.output_config = output_config_phy

        # Layer 0
        self.l0_coincidence_modules = l0_coincidence_modules = []
        for idx in range(l0_num):
            l0_module = RtioCoincidenceTriggerGenerator(
                    name=f"l0_{idx}",
                    generators=l0_trigger_generators,
                    reset_pulse_length=50,
                    pulse_max_length=255)
            l0_coincidence_modules.append(l0_module)
            setattr(self.submodules, f"module_l0_{idx}", l0_module)
            self.add_rtio_channels(
                channel=Channel.from_phy(l0_module),
                device_id=f"{module_identifier}_l0_{idx}",
                module="mcord_daq.coredevice.wrappers",
                class_name="RtioCoincidenceTriggerGeneratorWrapper",
                arguments={
                    "mask_mapping": l0_module.get_mask_mapping(),
                    "identifier": f"{module_identifier}_l0_{idx}"
                })

        trigger_lines = []
        trigger_counters = []
        trigger_labels = []

        self.l1_coincidence_modules = l1_coincidence_modules = []
        for idx in range(l1_num):
            # L1 coincidence module
            l1_module = RtioCoincidenceTriggerGenerator(
                    name=f"l1_{idx}",
                    generators=l0_coincidence_modules,
                    reset_pulse_length=50,
                    pulse_max_length=255)
            l1_coincidence_modules.append(l1_module)
            setattr(self.submodules, f"module_l1_{idx}", l1_module)
            self.add_rtio_channels(
                channel=Channel.from_phy(l1_module),
                device_id=f"{module_identifier}_l1_{idx}",
                module="mcord_daq.coredevice.wrappers",
                class_name="RtioCoincidenceTriggerGeneratorWrapper",
                arguments={
                    "mask_mapping": l1_module.get_mask_mapping(),
                    "identifier": f"{module_identifier}_l1_{idx}" 
                })

            trigger, trigger_counter = self._add_l1_output(
                l1_module.trigger, f"{module_identifier}_l1_{idx}")
            trigger_lines += [trigger]
            trigger_counters += [trigger_counter]
            trigger_labels += [f"l1_{idx}"]

        for module in l1_extra:
            for mod_trig in module.triggers:
                assert mod_trig['cd'] == "rio_phy"
                label = mod_trig['label']
                trigger, trigger_counter = self._add_l1_output(
                    mod_trig['signal'], f"{module_identifier}_l1_{label}")
                trigger_lines.append(trigger)
                trigger_counters.append(trigger_counter)
                trigger_labels += [label]
                
        # Output logic
        trigger_lines_array = Array(trigger_lines)
        trigger_counters_array = Array(trigger_counters)
        for output in outputs:
            l1_mask = getattr(output_config_phy, 
                "{}_l1_mask".format(output['label']))
            trigger_lines_vector = Cat(trigger_lines)
            trigger_lines_masked = Signal.like(trigger_lines_vector)
            self.comb += trigger_lines_masked.eq(l1_mask & trigger_lines_vector)
            output_select = Signal(max=max(len(trigger_lines), 2))
            priority_encoder = PriorityEncoder(len(trigger_lines_masked))
            self.submodules += priority_encoder
            self.comb += [
                priority_encoder.i.eq(trigger_lines_masked),
                output_select.eq(priority_encoder.o),
            ]
            self.sync.rio_phy += [
                output['trigger'].eq(0),
                If(trigger_lines_array[output_select] & ~priority_encoder.n,
                    output['trigger'].eq(trigger_lines_array[output_select]),
                    output['trigger_id'].eq(Cat(priority_encoder.o, trigger_counters_array[output_select])),
                )
            ]
        
        # Register core device
        self.register_coredevice(module_identifier, "mcord_daq.coredevice.trigger_controller", "TriggerController", arguments={
            "prefix": module_identifier,
            "l0_num": l0_num,
            "l1_num": l1_num,
            "output_config_csr": f"{module_identifier}_output_config",
            "l1_mask": trigger_labels,
            "reset_device": f"{module_identifier}_trigger_controller_reset"
        })

        if with_ila:
            for t, l, p in zip(self.l0_coincidence_modules[0].trigger_in_signals, 
                    self.l0_coincidence_modules[0].trigger_in_labels,
                    self.l0_coincidence_modules[0].pulses):
                self.submodules += [
                    ILAProbe(t, f"dbg_{l}_trig"),
                    ILAProbe(p, f"dbg_{l}_pulse")
                ]
            self.submodules += [ILAProbe(self.l0_coincidence_modules[0].pulse_length, "l0_0_pulse_length")]
            for idx, mod in enumerate(l0_coincidence_modules):
                self.submodules += [ILAProbe(mod.trigger, f"l0_trigger_{idx}")]
            for idx, mod in enumerate(l1_coincidence_modules):
                self.submodules += [ILAProbe(mod.trigger, f"l1_trigger_{idx}")]
            for idx, mod in enumerate(l1_extra):
                self.submodules += [ILAProbe(t['signal'], "l1_extra_{}".format(t['label'])) for t in mod.triggers]
            for output in outputs:
                self.submodules += [
                    ILAProbe(output['trigger'], "output_trigger_{}".format(output['label'])),
                    ILAProbe(output['trigger_id'], "output_trigger_id_{}".format(output['label']))
                ]


class MockTriggerGenerator(TriggerGenerator):

    def __init__(self, name):
        super().__init__(name)
        self.trigger = Signal(name=name)
        self.register_trigger(self.trigger, "trigger", "rio_phy")


def get_bus_signals(bus, bus_name="rtio"):
    signals = []
    def add_interface(iface, prefix):
        signals.append(iface.stb)
        iface.stb.name_override = f"{prefix}_stb"
        signals.append(iface.data)
        iface.data.name_override = f"{prefix}_data"
        if hasattr(iface, "address"):
            signals.append(iface.address)
            iface.address.name_override = f"{prefix}_address"

    add_interface(bus.o, f"{bus_name}_o")
    if bus.i is not None:
        add_interface(bus.i, f"{bus_name}_i")
    
    return signals


class SimulationWrapper(Module):

    def __init__(self):
        trigger_counter_len = 4
        l0_num=2
        l1_num=2
        trigger_id_len = 1 + trigger_counter_len

        self.clock_domains.rio_phy = cd = ClockDomain()

        trigger_generators = []
        trigger_signals = []
        for idx in range(4):
            tg = MockTriggerGenerator(f"trigger_in_{idx}")
            trigger_generators.append(tg)
            trigger_signals.append(tg.trigger)
            
        outputs = [
        {
            "label": f"output_{idx}", 
                "trigger": Signal(name=f"trigger_out_{idx}", reset=0), 
                "trigger_id": Signal(
                    trigger_id_len, 
                    name=f"trigger_out_id_{idx}",
                    reset=0
                )
            } for idx in range(4) 
        ]
        output_triggers = [o['trigger'] for o in outputs]
        output_trigger_ids = [o['trigger_id'] for o in outputs]

        dut = TriggerController(
            trigger_generators, 
            outputs,
            l0_num=l0_num,
            l1_num=l1_num,
            trigger_counter_len=trigger_counter_len,
            module_identifier="tc"
        )
        self.submodules.dut = dut

        self.io = {
            cd.clk,
            cd.rst,
            *trigger_signals,
            *output_triggers,
            *output_trigger_ids,
            *(get_bus_signals(dut.reset_phy.rtlink, "reset_phy_rtio")),
            *(get_bus_signals(dut.output_config.rtlink, "output_config_rtio"))
        }
        for idx, m in enumerate(dut.l0_coincidence_modules):
            self.io.update(get_bus_signals(m.rtlink, f"l0_{idx}_rtio"))
        for idx, m in enumerate(dut.l1_coincidence_modules):
            self.io.update(get_bus_signals(m.rtlink, f"l1_{idx}_rtio"))


if __name__ == "__main__":

    from migen.build.xilinx import common
    from elhep_cores.simulation.common import update_tb

    module = SimulationWrapper()
    so = dict(common.xilinx_special_overrides)
    so.update(common.xilinx_s7_special_overrides)

    verilog.convert(fi=module,
                    name="top",
                    special_overrides=so,
                    ios=module.io,
                    create_clock_domains=False).write('dut.v')
    update_tb('dut.v')
