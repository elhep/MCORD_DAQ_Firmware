from artiq.experiment import *
from artiq.language.units import ns, us

from base_experimenet import BaseMCORDExperiment


class Initialize(BaseMCORDExperiment, Experiment):

    cfd_offset = {
        "dac0": [
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3
        ],
        "dac1": [
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3,
            0xFFF//3
        ]
    }

    PULSE_LENGTH = 20

    pulse_length = {
        "fmc1_adc0_daq0_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq0_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq1_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq1_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq2_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq2_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq3_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq3_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq4_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq4_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq5_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq5_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq6_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq6_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc0_daq7_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc0_daq7_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq0_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq0_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq1_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq1_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq2_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq2_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq3_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq3_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq4_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq4_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq5_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq5_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq6_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq6_baseline_tg_fe": PULSE_LENGTH,
        "fmc1_adc1_daq7_baseline_tg_re": PULSE_LENGTH,
        "fmc1_adc1_daq7_baseline_tg_fe": PULSE_LENGTH
    }

    OFFSET_LEVEL = 0x3FF*0.5

    offset_levels = {
        "fmc1_adc0_ch0_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch1_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch2_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch3_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch4_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch5_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch6_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc0_ch7_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch0_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch1_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch2_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch3_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch4_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch5_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch6_baseline_tg": OFFSET_LEVEL,
        "fmc1_adc1_ch7_baseline_tg": OFFSET_LEVEL
    }

    trigger_channel_enabled = {
        "fmc1_adc0_daq0": True,
        "fmc1_adc0_daq1": True,
        "fmc1_adc0_daq2": True,
        "fmc1_adc0_daq3": True,
        "fmc1_adc0_daq4": True,
        "fmc1_adc0_daq5": True,
        "fmc1_adc0_daq6": True,
        "fmc1_adc0_daq7": True,
        "fmc1_adc1_daq0": True,
        "fmc1_adc1_daq1": True,
        "fmc1_adc1_daq2": True,
        "fmc1_adc1_daq3": True,
        "fmc1_adc1_daq4": True,
        "fmc1_adc1_daq5": True,
        "fmc1_adc1_daq6": True,
        "fmc1_adc1_daq7": True
    }

    coincidence = {
        "fmc1_adc1_daq4": ["fmc1_adc1_daq4_baseline_tg_re", "fmc1_adc1_daq5_baseline_tg_re"],
        "fmc1_adc0_daq0": ["fmc1_adc1_daq4_baseline_tg_re", "fmc1_adc1_daq5_baseline_tg_re"]
    }

    def run(self):
        print("Initializing FMC")
        self.initialize_fmc()

        print("Checking clocks")
        self.get_frequency(self.fmc1, "clk0")
        self.get_frequency(self.fmc1, "clk1")
        self.get_frequency(self.fmc1, "adc0_lclk")
        self.get_frequency(self.fmc1, "adc1_lclk")

        print("Setting CFD offsets")
        for i in range(8):
            self.fmc1_cfd_offset_dac0.set_mu(i, self.cfd_offset["dac0"][i])
            self.fmc1_cfd_offset_dac1.set_mu(i, self.cfd_offset["dac1"][i])

        print("Setting pulse lengths")
        for k, v in self.pulse_length.items():
            self.trigger_controller.set_pulse_length(k, v)
        
        print("Setting offset levels")
        for k, v in self.offset_levels.items():
            getattr(self, k).offset_level.write(int(v))
        
        print("Setting conincidence detection")
        for k, v in self.coincidence.items():
            self.trigger_controller.setup_coincidence(k, *v)

        print("Setting channel enables")
        for k, v in self.trigger_channel_enabled.items():
            self.trigger_controller.set_trigger_state(k, v)


        

