from artiq.experiment import *
from artiq.language.core import rpc, now_mu
from artiq.language.units import ns, us
from pprint import pprint
from itertools import product
import queue
import time


class TestDaqBandwidth(EnvExperiment):

    def build(self):
        self.setattr_device("core")

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
        
        self.setattr_device("fmc1_trigger_reset")
        self.setattr_device("trigger_controller")
        self.daq = self.fmc1_adc1_daq4

        self.samples = []

    @kernel
    def configure_adc(self):
        self.core.break_realtime()
        for adc_daq in self.adc_daqs:
            adc_daq.configure_rt(10,90)
            # adc_daq.clear_fifo()

    def configure(self):
        self.configure_adc()
        for adc_idx, daq_idx in product(range(2), range(8)):
            self.trigger_controller.setup_coincidence(f"fmc1_adc{adc_idx}_daq{daq_idx}", 
                "fmc1_adc1_daq4_baseline_tg_re")
            self.trigger_controller.set_trigger_state(f"fmc1_adc{adc_idx}_daq{daq_idx}", True)       

    @rpc(flags={"async"})
    def store_samples(self, channel, samples):
        self.samples.append((channel, samples))

    @kernel
    def transfer_data_from_rtio(self, gate_close_time):
        while self.core.get_rtio_counter_mu() < gate_close_time:
            for daq_idx in range(len(self.adc_daqs)):
                daq = self.adc_daqs[daq_idx]
                data_idx = daq.get_samples(8*us)
                self.store_samples(daq_idx, daq.data_buffer[:data_idx])

    @kernel
    def acquire(self, gate_time):
        self.core.break_realtime()
        # Make sure triggers are in reset
        self.fmc1_trigger_reset.on()
        for daq in self.adc_daqs:
            daq.clear_fifo()
        print("RTIO buffers cleared, starting DAQ...")
        self.core.break_realtime()
        gate_open_time = self.core.get_rtio_counter_mu()
        gate_close_time = gate_open_time + self.core.seconds_to_mu(gate_time)
        with parallel:
            with sequential:
                delay(10*ms)
                self.fmc1_trigger_reset.off()
                delay(gate_time-10*ms)
                self.fmc1_trigger_reset.on()
            self.transfer_data_from_rtio(gate_close_time)

    def run(self):
        # self.configure()
        t0 = time.time()
        try:
            self.acquire(5*s)
        except RTIOOverflow:
            print("Lost samples!")
        print(time.time()-t0)

    @staticmethod
    def decode_sample(sample, data_width=10):
        data_mask = 2**data_width-1
        data = sample & data_mask
        trigger_cnt = sample >> data_width
        return (trigger_cnt, data)

    @staticmethod
    def divide_in_triggers(ch_data):
        if not ch_data:
            return []
        triggers = []
        current_trigger_idx = ch_data[0][0]
        current_trigger_samples = []
        for d in ch_data:
            if d[0] == current_trigger_idx:
                current_trigger_samples.append(d[1])
            else:
                triggers.append({
                    "trigger_id": current_trigger_idx,
                    "samples": current_trigger_samples
                })
                current_trigger_samples = []
                current_trigger_idx = d[0]
        return triggers
        
    def analyze(self):
        channel_samples = [[] for _ in range(16)]
        for s in self.samples:
            ch_data = [self.decode_sample(s) for s in s[1]]
            ch_data = self.divide_in_triggers(ch_data)
            channel_samples[s[0]] += ch_data

        for ch_idx, ch_data in enumerate(channel_samples):
            channel_triggers = [x['trigger_id'] for x in ch_data]
            print(ch_idx, len(channel_triggers))

        # pprint(channel_samples)
        # with open("samples.txt", "w+") as f:
        #     for s in channel_samples:
        #         f.write(str(s) + "\n")
            
