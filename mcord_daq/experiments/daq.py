import queue
import csv
import threading
from artiq.coredevice.exceptions import RTIOOverflow

from artiq.experiment import *
from artiq.language.core import at_mu, now_mu
from artiq.language.units import ns, us, s

from mcord_daq.coredevice.samples_writer import *
from mcord_daq.experiments.base_experimenet import BaseMCORDExperiment


class TriggeringSelfTest(BaseMCORDExperiment, Experiment):

    @kernel
    def freeze(self):
        self.core.break_realtime()
        self.trigger_controller.reset.on()

    @kernel
    def unfreeze(self):
        self.core.break_realtime()
        self.trigger_controller.reset.off()

    @kernel
    def configure_tg_offsets(self):
        self.core.break_realtime()
        self.fmc1_adc0_ch2_baseline_tg.offset_level.write(0x33a)
        self.fmc1_adc0_ch3_baseline_tg.offset_level.write(0x0c4)

    def configure_triggers(self):        
        # L0/0 detects coincidence of ch2/re with ch3/fe
        vd0 = self.trigger_controller.l0_modules[0]
        vd0.disable_all_sources()
        vd0.set_pulse_length(20)
        vd0.enable_source(*vd0.mask_mapping["fmc1_adc0_ch2_baseline_tg_re"])
        vd0.enable_source(*vd0.mask_mapping["fmc1_adc0_ch3_baseline_tg_fe"])
        vd0.set_enabled(1)

        # L0/1 detects coincidence of ch2/fe with ch3/re
        vd1 = self.trigger_controller.l0_modules[1]
        vd1.disable_all_sources()
        vd1.set_pulse_length(20)
        vd1.enable_source(*vd1.mask_mapping["fmc1_adc0_ch2_baseline_tg_fe"])
        vd1.enable_source(*vd1.mask_mapping["fmc1_adc0_ch3_baseline_tg_re"])
        vd1.set_enabled(1)

        # L1/0 trigger on single input from L0/0
        vd1 = self.trigger_controller.l1_modules[0]
        vd1.disable_all_sources()
        vd1.set_pulse_length(20)
        vd1.enable_source(*vd1.mask_mapping["l0_0_trigger"])
        vd1.set_enabled(1)

        # L1/1 trigger on single input from L0/1
        vd1 = self.trigger_controller.l1_modules[1]
        vd1.disable_all_sources()
        vd1.set_pulse_length(20)
        vd1.enable_source(*vd1.mask_mapping["l0_1_trigger"])
        vd1.set_enabled(1)
        
        # Configure ADC0/2 to be triggered with L1/0 or L1/1
        self.trigger_controller.disable_all_output_sources(
            "fmc1_adc0_daq2_l1_mask")
        self.trigger_controller.enable_output_source(
            "fmc1_adc0_daq2_l1_mask", "l1_0")
        # self.trigger_controller.enable_output_source(
        #     "fmc1_adc0_daq2_l1_mask", "l1_1")

        # Configure ADC0/3 to be triggered with L1/0 or L1/1
        self.trigger_controller.disable_all_output_sources(
            "fmc1_adc0_daq3_l1_mask")
        self.trigger_controller.enable_output_source(
            "fmc1_adc0_daq3_l1_mask", "l1_1")
        # self.trigger_controller.enable_output_source(
        #     "fmc1_adc0_daq3_l1_mask", "l1_1")

    def configure_hw(self, daqs, pretrigger, posttrigger):
        self.freeze()
        self.configure_tg_offsets()
        self.configure_triggers()
        self.configure_daq(daqs, pretrigger, posttrigger)

    @kernel
    def configure_daq(self,daqs, pretrigger, posttrigger):
        self.core.break_realtime()
        for daq in daqs:
            daq.configure_rt(pretrigger, posttrigger)
        
        for daq in daqs:
            daq.clear_fifo()
       
    @kernel
    def daq_transfer_loop(self, daqs, duration, chunk=200):
        end_time = \
            self.core.get_rtio_counter_mu() + self.core.seconds_to_mu(duration)
        while self.core.get_rtio_counter_mu() < end_time:
            for daq in daqs:
                daq.transfer_samples(chunk)

    @kernel
    def run_daq(self, duration, daqs, chunk=200):
        self.core.break_realtime()
        self.trigger_controller.reset.off()
        at_mu(now_mu() + self.core.seconds_to_mu(duration))
        self.trigger_controller.reset.on()
        self.daq_transfer_loop(daqs, duration, chunk)
                      
    def run(self):
        duration = 10*s
        chunks = 200

        daq_channels = [
            {"type": "adc", "channel": 2, "daq": self.fmc1_adc0_daq2},
            {"type": "adc", "channel": 3, "daq": self.fmc1_adc0_daq3},
            # {"type": "tdc", "channel": 2, "daq": self.fmc1_tdc0_daq2},
            # {"type": "tdc", "channel": 3, "daq": self.fmc1_tdc0_daq3}            
        ]
        daqs = [channel["daq"] for channel in daq_channels]
        data_writer = CSVSamplesWriter(daq_channels, "output.csv")
        
        self.configure_hw(daqs, 100, 20)
        data_writer.start()
        try:
            self.run_daq(duration, daqs, chunks)
        except RTIOOverflow as e:
            print("!"*80)
            print("Lost samples!")
            print(e)
            print("!"*80)
        finally:
            data_writer.stop()
