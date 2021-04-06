from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")
        self.setattr_device("fmc1_tdc1_ch4_baseline_tg")

        self.fmc1 = self.get_device("fmc1")  # type: FmcAdc100M10bTdc16cha
    
    def run(self):
        # Assuming FMC is already initialized

        # 0x1FF is signal baseline, let's have trigger level in Vpp quarter
        self.fmc1_tdc1_ch4_baseline_tg.offset_level.write(int(0x3FF*0.75))


        

