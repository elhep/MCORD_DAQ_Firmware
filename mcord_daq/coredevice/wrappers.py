from random import sample
from artiq.language.core import kernel, delay, delay_mu, portable, rpc
from artiq.language.units import ns
from artiq.coredevice.rtio import rtio_output, rtio_input_data

from elhep_cores.coredevice.trigger_generators import (
    RtioCoincidenceTriggerGenerator
)
from elhep_cores.coredevice.circular_daq import CircularDaq


class RtioBaselineTriggerGenerator:

    kernel_invariants = {"core", "identifier", "index", "csr"}

    def __init__(self, dmgr, csr_device, prefix, index, core_device="core"):
        self.core = dmgr.get(core_device)
        self.csr = dmgr.get(csr_device)
        
        self.identifier = f"{prefix}_baseline_tg"
        self.index = index

    @property
    def rising_edge(self):
        return self.identifier + "_re"

    @property
    def falling_edge(self):
        return self.identifier + "_fe"

    def set_offset(self, value):
        self.csr.offset_level.write(value)

class RtioCoincidenceTriggerGeneratorWrapper(RtioCoincidenceTriggerGenerator):

    def __init__(self, dmgr, mask_mapping, channel, identifier, 
            core_device="core"):
        self.identifier = identifier
        super().__init__(dmgr, mask_mapping, channel, core_device)

    @property
    def trigger(self):
        return self.identifier


class MCORDCircularDaq(CircularDaq):

    def __init__(self, dmgr, channel, data_mapping, buffer_len=1024, 
            core_device="core"):
        super().__init__(dmgr, channel, buffer_len=buffer_len, 
            core_device=core_device)
        
        self.sample_processor = self.get_sample_processor(data_mapping)
        self.queue = None

    @staticmethod
    def get_sample_processor(data_mapping):
        """Data mapping format:
        LSB
        [
            ("id string", width),
            ("id string", width),
            ...
        ]
        MSB
        """
        # TODO: Move to ctype struct?
        labels = []
        masks = []
        offsets = []
        current_offset = 0
        for label, width in data_mapping:
            labels.append(label)
            masks.append((1<<width)-1)
            offsets.append(current_offset)
            current_offset += width

        def sample_processor(sample):
            output = {}
            for label, mask, offset in zip(labels, masks, offsets):
                output[label] = (sample >> offset) & mask
            output["readout"] = sample
            return output

        return sample_processor

    @rpc(flags={"async"})
    def store(self, samples):
        self.queue.put([self.sample_processor(s) for s in samples])
        # self.queue.put(samples)