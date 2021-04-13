from artiq.language.core import kernel, delay, portable
from artiq.language.units import ns
from artiq.coredevice.rtio import rtio_output, rtio_input_data
from artiq.language.types import TInt32
import json
import numpy as np


class TriggerController:
    
    # kernel_invariants = ["layout"]

    def __init__(self, dmgr, channel, layout, core_device="core"):
        self.channel = channel
        self.core = dmgr.get(core_device)
        self.ref_period_mu = self.core.seconds_to_mu(
            self.core.coarse_ref_period)

        with open(layout, 'r') as f:
            self.layout = json.load(f)
        self.adr_per_mask = (len(self.layout["mask_layout"])+31)//32

    @kernel
    def write(self, address, data):
        self.core.break_realtime()
        rtio_output((self.channel << 8) | address << 1 | 1, data)

    @kernel
    def read(self, address) -> TInt32:
        self.core.break_realtime()
        rtio_output((self.channel << 8) | address << 1 | 0, 0)
        return rtio_input_data(self.channel)

    def setup_coincidence(self, output_channel, *input_channels):
        mask_address = self.layout["output_channels"][output_channel]["mask_address"]
        mask = [0]*self.adr_per_mask
        for channel in input_channels:
            ch_cfg = self.layout["mask_layout"][channel]
            adr_offset = ch_cfg["address_offset"]
            bit_offset = ch_cfg["bit_offset"]
            mask[adr_offset] |= 1 << bit_offset
        for i, m in enumerate(mask):
            self.write(mask_address+i, m)

    def set_trigger_state(self, output_channel, enabled):
        en_offset = self.layout["output_channels"][output_channel]["en_offset"]
        en_bit_offset = self.layout["output_channels"][output_channel]["en_bit_offset"]
        old_value = self.read(en_offset)
        old_value &= ~((1 << en_bit_offset))
        old_value |= int(bool(enabled)) << en_bit_offset
        self.write(en_offset, np.int32(old_value))

    def set_pulse_length(self, input_channel, value):
        assert value < 255
        ch_cfg = self.layout["mask_layout"][input_channel]
        pulse_length_offset = ch_cfg["pulse_length_offset"]
        self.write(pulse_length_offset, value)
