from artiq.language.core import kernel, delay, portable, rpc
from artiq.language.units import ns
from artiq.coredevice.rtio import rtio_output, rtio_input_data
from artiq.language.types import TInt32
import json
import numpy as np


class TriggerController:

    kernel_invariants = {"l0_modules", "l1_modules", "output_config", 
        "l1_mask"}

    def __init__(self, dmgr, l0_num, l1_num, prefix, output_config_csr, 
            l1_mask, reset_device, core_device="core"):
        self.core = dmgr.get(core_device)
        self.l0_modules = \
            [dmgr.get(f"{prefix}_l0_{idx}") for idx in range(l0_num)]
        self.l1_modules = \
            [dmgr.get(f"{prefix}_l1_{idx}") for idx in range(l1_num)]
        self.output_config = dmgr.get(output_config_csr)
        self.l1_mask = {label: idx for idx, label in enumerate(l1_mask)}
        self.reset = dmgr.get(reset_device)

    @kernel
    def _do_enable_output_source(self, output_reg, source_idx):
        self.core.break_realtime()
        value = output_reg.read_rt()
        value |= 1 << source_idx
        output_reg.write(value)

    @kernel
    def _do_disable_all_output_sources(self, output_reg):
        self.core.break_realtime()
        output_reg.write(0)

    def disable_all_output_sources(self, output):
        mask_reg = getattr(self.output_config, output)
        self._do_disable_all_output_sources(mask_reg)

    def enable_output_source(self, output, source):
        mask_reg = getattr(self.output_config, output)
        source_idx = self.l1_mask[source]
        self._do_enable_output_source(mask_reg, source_idx)
        
        

    
        
        
        
        
    #     # Key is an expression for input triggers and value is a channel number
    #     self.l0_config = {}
    #     self.l1_config = {}

    #     self.l0_free_controllers = {dmgr.get(f"{prefix}_l0_{idx}") for idx in range(l0_num)}
    #     self.l1_free_controllers = {dmgr.get(f"{prefix}_l1_{idx}") for idx in range(l1_num)}

    # def set_coincidence(self, layer, *identifiers):
    #     assert layer in [0, 1], "Invalid coincidence target!"
    #     sources = sorted(identifiers)
    #     expression = "|".join(sources)
    #     config = getattr(self, f"l{layer}_config")
    #     free_controllers = getattr(self, f"l{layer}_free_controllers")
    #     if expression not in config:
    #         if len(free_controllers) == 0:
    #             raise RuntimeError(f"l{layer} has no more free controllers!")
    #         controller = free_controllers.pop()
    #         controller.enable_source(*sources)
    #         config[expression] = controller
    #         return controller
    #     else:
    #         return config[expression]

    # def set_detector_coincidence(self, *detectors):
    #     # This function operates on L1
    #     identifiers = [d.coincidence_controller.identifier for d in detectors]
    #     controller = self.set_coincidence(1, *identifiers)
    #     return controller

    # def set_trigger_source(self, source, *identifiers):
    #     for identifier in identifiers:
    #         getattr(self.output_config, f"{identifier}_output_select").write(source.index)

    # def enable_output(self, state, *identifiers):
    #     for identifier in identifiers:
    #         getattr(self.output_config, f"{identifier}_output_enable").write(state)

    # def create_coincidence_group(self, *detectors):
    #     controller = self.set_detector_coincidence(*detectors)
    #     identifiers = []
    #     for detector in detectors:
    #         identifiers.append(detector.identifiers)
    #     self.set_trigger_source(controller, *identifiers)
