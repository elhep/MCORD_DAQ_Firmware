from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")
        self.setattr_device("fmc1_cfd_offset_dac0")
        self.setattr_device("fmc1_cfd_offset_dac1")
        self.setattr_device("fmc1_tdc1_ch4_baseline_tg")

        self.fmc1 = self.get_device("fmc1")  # type: FmcAdc100M10bTdc16cha

    @kernel
    def debug_adc_interface(self, pattern, adc=0):
        self.core.break_realtime()
        if pattern < 0:
            self.fmc1.adc[adc].enable_ramp_test_pattern()    
        else:
            self.fmc1.adc[adc].enable_test_pattern(pattern)

    @kernel
    def test_daq(self, adc=0, daq=0):
        self.core.break_realtime()
        self.fmc1.adc[adc].enable_ramp_test_pattern()
        self.fmc1.adc[adc].daq[daq].clear_fifo()
        self.fmc1.adc[adc].daq[daq].configure(32, 32)
        delay(100 * us)
        self.fmc1.adc[adc].daq[daq].trigger()
        delay(10000 * us)
        self.fmc1.adc[adc].daq[daq].get_samples()

    @kernel
    def debug_daq(self):
        self.core.break_realtime()
        self.fmc1.adc[0].daq[8].configure(20, 20)

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
        
    def read_tdc(self, tdc):
        self.fmc1.tdc[tdc].read_results()
        results = self.fmc1.tdc[tdc].spi_readout
        print(f"TDC: {tdc}")
        print("="*60)
        for ch in range(4):
            ref_idx = results[ch*6+0] << 16 | results[ch*6+1] << 8 | results[ch*6+2]
            stop =    results[ch*6+3] << 16 | results[ch*6+4] << 8 | results[ch*6+5]
            print(f"CH{ch} REF IDX: {ref_idx} STOP: {stop}")
        print()

    def run(self):
        while True:
            for i in range(4):
                self.fmc1.tdc[i].start_measurement()       
