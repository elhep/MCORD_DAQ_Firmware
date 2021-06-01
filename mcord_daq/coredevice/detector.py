class Detector:

    @staticmethod
    def _channel_to_adc_loc(channel):
        adc_idx = 0 if channel <= 7 else 1
        adc_ch = 7 - (channel-4) % 8
        return adc_idx, adc_ch

    def __init__(self, dmgr, fmc, channel_a, channel_b, coincidence_module, 
            trigger_controller, core_device="core"):
        self.core = dmgr.get(core_device)
        self.ref_period_mu = \
            self.core.seconds_to_mu(self.core.coarse_ref_period)

        adc_a = self._channel_to_adc_loc(channel_a)
        adc_b = self._channel_to_adc_loc(channel_b)

        self.baseline_tg_a = dmgr.get(f"{fmc}_adc{adc_a[0]}_ch{adc_a[1]}")
        self.baseline_tg_a_id = f"{fmc}_adc{adc_a[0]}_ch{adc_a[1]}_{{edge}}"
        self.baseline_tg_b = dmgr.get(f"{fmc}_adc{adc_b[0]}_ch{adc_b[1]}")
        self.baseline_tg_b_id = f"{fmc}_adc{adc_b[0]}_ch{adc_b[1]}_{{edge}}"

        self.cfd_dac_a = dmgr.get(f"{fmc}_cfd_offset_dac{0 if channel_a <= 7 else 1}")
        self.cfd_dac_ch_a = channel_a % 8
        self.cfd_dac_b = dmgr.get(f"{fmc}_cfd_offset_dac{0 if channel_b <= 7 else 1}")
        self.cfd_dac_ch_b = channel_b % 8

        self.adc_daq_a = dmgr.get(f"{fmc}_adc{adc_a[0]}_daq{adc_a[1]}")
        self.adc_daq_b = dmgr.get(f"{fmc}_adc{adc_b[0]}_daq{adc_b[1]}")

        tdc_a = (channel_a // 4, channel_a % 4)
        tdc_b = (channel_b // 4, channel_b % 4)

        self.tdc_daq_a = dmgr.get(f"{fmc}_adc{tdc_a[0]}_daq{tdc_a[1]}")
        self.tdc_daq_b = dmgr.get(f"{fmc}_adc{tdc_b[0]}_daq{tdc_b[1]}")

        self.adc_daq_a_id = f"{fmc}_adc{adc_a[0]}_daq{adc_a[1]}_l1_mask"
        self.adc_daq_b_id = f"{fmc}_adc{adc_b[0]}_daq{adc_b[1]}_l1_mask"
        self.tdc_daq_a_id = f"{fmc}_tdc{tdc_a[0]}_daq{tdc_a[1]}_l1_mask"
        self.tdc_daq_b_id = f"{fmc}_tdc{tdc_b[0]}_daq{tdc_b[1]}_l1_mask"

        self.coincidence_module = dmgr.get(coincidence_module)
        self.trigger_controller = dmgr.get(trigger_controller)

    def init(self, trigger_level_a_mu, trigger_level_b_mu, cfd_level_a_mu, cfd_level_b_mu,
            coincidence_window_ns, edge="fe"):
        self.baseline_tg_a.offset_level.write(trigger_level_a_mu)
        self.baseline_tg_b.offset_level.write(trigger_level_b_mu)
        self.cfd_dac_a.set_mu(self.cfd_dac_ch_a, cfd_level_a_mu)
        self.cfd_dac_b.set_mu(self.cfd_dac_ch_b, cfd_level_b_mu)
        
        self.coincidence_module.disable_all_sources()
        pulse_length_mu = (coincidence_window_ns+7)//8
        self.coincidence_module.set_pulse_length(pulse_length_mu)
        self.coincidence_module.enable_source(
            *self.coincidence_module.mask_mapping[self.baseline_tg_a_id.format(edge=edge)])
        self.coincidence_module.enable_source(
            *self.coincidence_module.mask_mapping[self.baseline_tg_b_id.format(edge=edge)])
        self.coincidence_module.set_enabled(1)

    def enable_daq(self, l1_idx):
        self.trigger_controller.disable_all_output_sources(self.adc_daq_a_id)
        self.trigger_controller.disable_all_output_sources(self.adc_daq_b_id)
        self.trigger_controller.disable_all_output_sources(self.tdc_daq_a_id)
        self.trigger_controller.disable_all_output_sources(self.tdc_daq_b_id)

        self.trigger_controller.enable_output_source(self.adc_daq_a_id, f"l1_{l1_idx}")
        self.trigger_controller.enable_output_source(self.adc_daq_b_id, f"l1_{l1_idx}")
        self.trigger_controller.enable_output_source(self.tdc_daq_a_id, f"l1_{l1_idx}")
        self.trigger_controller.enable_output_source(self.tdc_daq_b_id, f"l1_{l1_idx}")