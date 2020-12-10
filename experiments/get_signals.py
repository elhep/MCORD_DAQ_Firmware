from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint
from coredevice.fmc_adc100M_10b_tdc_16cha import FmcAdc100M10bTdc16cha
import json
import random


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")
        self.fmc1 = self.get_device("fmc1")  # type: FmcAdc100M10bTdc16cha
        self.adc = 0

    @kernel
    def initialize(self):
        self.core.break_realtime()
        self.fmc1.initialize()
    
    @kernel
    def setup(self, adc):
        self.core.break_realtime()
        self.fmc1.adc[adc].enable_ramp_test_pattern()
        for i in range(8):
            self.fmc1.adc[adc].daq[i].clear_fifo()
            self.fmc1.adc[adc].daq[i].configure(100 , 100)

    @kernel
    def trigger(self, adc):
        self.core.break_realtime()
        for i in range(8):
            self.fmc1.adc[adc].daq[i].trigger()
    
    @kernel
    def get_samples(self, adc):
        self.core.break_realtime()
        for i in range(8):
            self.fmc1.adc[adc].daq[i].get_samples()

    def run(self):
        # self.initialize()
        self.setup(self.adc)
        self.trigger(self.adc)
        self.get_samples(self.adc)

    def analyze(self):
        results = {"adc": self.adc}
        for i in range(8):
            results[f"ch{i}"] = [int(x) for x in self.fmc1.adc[self.adc].daq[i].samples]
        print(json.dumps(results))
        # from pprint import pprint
        # pprint(results)
        
    







