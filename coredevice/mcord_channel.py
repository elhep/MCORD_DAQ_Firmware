from artiq.language.units import ns, us
from artiq.language.core import kernel


class McordChannel:

    def __init__(self, dmgr, fmc, fmc_channel, adc_daq, tdc_daq, baseline_tg, core_device="core"):
        self.core = dmgr.get(core_device)
        self.ref_period_mu = self.core.seconds_to_mu(
            self.core.coarse_ref_period)

        self.fmc = fmc
        self.fmc_channel = fmc_channel
        self.adc_daq = adc_daq
        self.tdc_daq = tdc_daq
        self.baseline_tg = baseline_tg

        

        