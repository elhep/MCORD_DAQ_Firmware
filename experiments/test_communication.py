from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint
from coredevice.fmc_adc100M_10b_tdc_16cha import FmcAdc100M10bTdc16cha


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")

        self.fmc1 = self.get_device("fmc1")  # type: FmcAdc100M10bTdc16cha

    @kernel
    def test_daq(self, adc=0, daq=0):
        self.core.break_realtime()
        self.fmc1.adc[adc].enable_test_pattern(0x123)
        self.clear_adc_rtio()
        self.fmc1.adc[adc].daq[daq].clear_fifo()
        self.fmc1.adc[adc].daq[daq].configure(20, 20)
        delay(100 * us)
        self.fmc1.adc[adc].daq[daq].trigger()
        delay(100 * us)
        self.fmc1.adc[adc].daq[daq].get_samples()

    @kernel
    def clear_adc_rtio(self):
        self.fmc1.adc[1].daq[0].clear_fifo()

    @kernel
    def debug_daq(self):
        self.core.break_realtime()
        self.fmc1.adc[1].daq[8].configure(20, 20)

    @kernel
    def initialize(self):
        self.core.break_realtime()
        self.fmc1.initialize()
    
    def get_frequency(self, fmc, channel_prefix):
        ttl = getattr(fmc, f"{channel_prefix}_ttl")
        edge_counter = getattr(fmc, f"{channel_prefix}_edge_counter")
        print(f"{channel_prefix} : {self.get_freq(ttl, edge_counter)/1000} MHz")

    @kernel
    def get_freq(self, ttl, edge_counter):
        self.core.break_realtime()
        ttl.input()
        delay(1*ms)
        edge_counter.gate_rising(1*ms)
        delay(2*ms)
        return edge_counter.fetch_count()

    @kernel
    def set_delay(self, val):
        self.core.break_realtime()
        self.fmc1.adc[0].phy.adclk_delay_value.write_rt(val)
        
    def run(self):
        self.initialize()
        self.get_frequency(self.fmc1, "clk0")
        self.get_frequency(self.fmc1, "clk1")
        self.get_frequency(self.fmc1, "adc0_lclk")
        self.get_frequency(self.fmc1, "adc1_lclk")
        
        # for i in range(32):
        #     self.set_delay(i)
        #     input(f"{i} [ENTER]")


        # self.test_daq(adc=0)
        





