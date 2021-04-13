from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1_adc1_daq4")
        self.setattr_device("fmc1_trigger_reset")
        self.daq = self.fmc1_adc1_daq4

    @kernel
    def acquire(self):
        self.core.break_realtime()
        # self.fmc1_trigger_reset.pulse(1*us)

        self.daq.configure(100, 100)
        self.daq.clear_fifo()
        # self.daq.trigger()
        self.daq.get_samples(10*s)

    def run(self):
        self.acquire()
        print(self.daq.samples)

