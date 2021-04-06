from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1_adc1_daq4")
        self.daq = self.fmc1_adc1_daq4

    @kernel
    def acquire(self):
        self.core.break_realtime()
        self.daq.configure(20, 20)
        self.daq.trigger()
        self.daq.clear_fifo()
        self.daq.get_samples()

    def run(self):
        self.acquire()
        print(self.samples)

