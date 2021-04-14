from itertools import product

from artiq.experiment import *
from artiq.language.units import ns, us


class BaseMCORDExperiment(HasEnvironment):

    def build(self):
        
        self.setattr_device("core")
        self.setattr_device("fmc1")
        self.setattr_device("trigger_controller")

        tg_channels = []
        for adc, ch in product(range(2), range(8)):
            dev_name = f"fmc1_adc{adc}_ch{ch}_baseline_tg"
            self.setattr_device(dev_name)
            tg_channels.append(dev_name)

        self.setattr_device("fmc1_cfd_offset_dac0")
        self.setattr_device("fmc1_cfd_offset_dac1")

        self.adc_daqs = []
        for adc_idx, daq_idx in product(range(2), range(8)):
            daq_name = f"fmc1_adc{adc_idx}_daq{daq_idx}"
            self.setattr_device(daq_name)
            self.adc_daqs.append(getattr(self, daq_name))

        self.tdc_daqs = []
        for tdc_idx, daq_idx in product(range(4), range(4)):
            daq_name = f"fmc1_tdc{tdc_idx}_daq{daq_idx}"
            self.setattr_device(daq_name)
            self.tdc_daqs.append(getattr(self, daq_name))

    @kernel
    def initialize_fmc(self):
        self.core.break_realtime()
        self.fmc1.initialize()

        for i in range(4):
            self.fmc1.tdc[i].start_measurement()

    @kernel
    def get_freq(self, ttl, edge_counter):
        self.core.break_realtime()
        ttl.input()
        delay(1*ms)
        edge_counter.gate_rising(1*ms)
        delay(2*ms)
        return edge_counter.fetch_count()

    def get_frequency(self, fmc, channel_prefix):
        ttl = getattr(fmc, f"{channel_prefix}_ttl")
        edge_counter = getattr(fmc, f"{channel_prefix}_edge_counter")
        print(f"{channel_prefix} : {self.get_freq(ttl, edge_counter)/1000} MHz")