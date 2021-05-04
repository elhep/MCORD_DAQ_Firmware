from artiq.language.units import ns, us
from artiq.language.core import kernel


class McordChannel:

    def __init__(self, dmgr, adc_daq, tdc_daq, trigger_generator, 
            cfd_offset_dac, cfd_offset_dac_ch, trigger_output_idx, 
            core_device="core"):
        self.core = dmgr.get(core_device)
        self.ref_period_mu = \
            self.core.seconds_to_mu(self.core.coarse_ref_period)
        self.adc_daq = dmgr.get(adc_daq)
        self.tdc_daq = dmgr.get(tdc_daq)
        self.trigger_generator = dmgr.get(trigger_generator)
        self.cfd_offset_dac = dmgr.get(cfd_offset_dac)
        self.cfd_offset_dac_ch = cfd_offset_dac_ch
        self.trigger_output_idx = trigger_output_idx

        

        

        