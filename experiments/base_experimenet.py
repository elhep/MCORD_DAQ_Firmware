from artiq.experiment import *
from artiq.language.units import ns, us


class SAS:




def mcx_sas_adapter(sas):



# SAS1 (J13) | SAS0 (J12) | TRIG | CLK



class MCORDChannel:

    def __init__(self, uid, fmc, tdc_daq, adc_daq, baseline_tg):
        self.uid = uid
        self.fmc = fmc
        self.fmc_ch_idx = fmc_ch_idx


class BaseMCORDExperiment(EnvExperiment):

    def __init__(self):
        
        self.setattr_device("core")
        self.setattr_device("fmc1")

        self.channels = [
            MCORDChannel("fmc1_j12_tx0", fmc1, )
        ]

        self.mcx_sas_adapter_channels = [
            # Channels
        ]
        self.fmc_channels = [
            # Channels
        ]