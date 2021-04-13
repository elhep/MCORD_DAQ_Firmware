from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")
        self.setattr_device("fmc1_tdc1_ch4_baseline_tg")
        self.setattr_device("fmc1_tdc1_ch5_baseline_tg")
        self.setattr_device("trigger_controller")
        self.setattr_device("fmc1_trigger_reset")
        
        self.fmc1 = self.get_device("fmc1")  # type: FmcAdc100M10bTdc16cha
    
    def run(self):
        # Assuming FMC is already initialized

        # 0x1FF is signal baseline, let's have trigger level in Vpp quarter
        self.fmc1_tdc1_ch4_baseline_tg.offset_level.write(int(0x3FF*0.5))
        self.fmc1_tdc1_ch5_baseline_tg.offset_level.write(int(0x3FF*0.5))

        self.trigger_controller.setup_coincidence("fmc1_adc1_daq4", 
            "fmc1_adc1_daq4_baseline_tg_re")
        self.trigger_controller.set_trigger_state("fmc1_adc1_daq4", True)

        self.trigger_controller.set_pulse_length("fmc1_adc1_daq4_baseline_tg_re", 100)


        

