from artiq.coredevice.rtio import rtio_output, rtio_input_data
from artiq.language import TInt32, TInt64
from artiq.language.core import kernel, delay_mu
from artiq.language.units import us, ns, ms
from numpy import int64, int32
import json


class TriggerChannel:

    def __init__(self, core, channel, base_address):
        self.core = core
        self.channel = channel
        self.base_address = base_address

    @kernel
    def enable(self, source):
        rtio_output(self.channel << 8 | (self.base_address + source['address_offset']) << 1 | 0, 0x0)
        prev_state = rtio_input_data(self.channel)
        prev_state |= (1 << source['word_offset'])
        rtio_output(self.channel << 8 | (self.base_address + source['address_offset']) << 1 | 1, prev_state)
    
    @kernel
    def enable(self, source):
        rtio_output(self.channel << 8 | (self.base_address + source['address_offset']) << 1 | 0, 0x0)
        prev_state = rtio_input_data(self.channel)
        prev_state &= ~(1 << self.offset)
        rtio_output(self.channel << 8 | (self.base_address + source['address_offset']) << 1 | 1, prev_state)

    @kernel
    def state(self, source):
        rtio_output(self.channel << 8 | (self.base_address + source['address_offset']) << 1 | 0, 0x0)
        prev_state = rtio_input_data(self.channel)
        return (prev_state >> source['word_offset']) & 0x1


class TriggerController:

    class Sources: pass

    def __init__(self, dmgr, channel, layout, core_device="core"):
        self.channel = channel
        self.core = dmgr.get(core_device)
        self.ref_period_mu = self.core.seconds_to_mu(
            self.core.coarse_ref_period)

        self.sources = self.Sources()
        
        with open(layout, "r") as f:
            layout = json.load(f)
        
        channel_config_layout = layout["channel_layout"]
        for k, v in channel_config_layout.items():
            setattr(self.sources, k, v)
        
        for ch_id in layout["channels"].keys():
            setattr(self, ch_id, TriggerChannel(self.core, self.channel, v))
        
        self.sw_triggers_addreses = [layout["sw_trigger_start"] + i for i in range(layout["sw_trigger_num"])]

    @kernel
    def sw_trigger(self, n):
        rtio_output((self.channel << 8) | self.sw_triggers_addreses[n] | 1, 1)
