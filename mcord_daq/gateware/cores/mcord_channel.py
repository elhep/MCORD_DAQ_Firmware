from migen import *

from mcord_daq.gateware.cores.mcord_daq_channel import MCORDDAQChannel
from mcord_daq.gateware.cores.coincidence_detector import CoincidenceDetector


class MCORDChannel(Module):

    def __init__(self, trigger_id_width, adc_data_width, tdc_data_width, circular_buffer_depth,
                 throttler_max_acquisitions):
        # CD: sys
        self.trigger_i = Signal()
        self.trigger_id_i = Signal(trigger_id_width)
        self.pretrigger_i = Signal(max=circular_buffer_depth)
        self.posttrigger_i = Signal(max=circular_buffer_depth)
        self.throttler_acq_num_i = Signal(max=throttler_max_acquisitions)
        self.throttler_acq_len_i = Signal(max=circular_buffer_depth)
        self.throttler_arm_i = Signal()
        self.throttler_rst_i = Signal()
        self.trigger_mode_i = Signal(11)
        self.trigger_level_i = Signal(adc_data_width)
        self.trigger_o = Signal()
        self.coincidence_detection_window_i = Signal(8)
        self.event_counter_enabled_i = Signal()
        self.event_counter_o = Signal(16)

        # CD: adc_dclk_a
        self.adc_data_a_i = Signal(adc_data_width)
        # CD: adc_dclk_b
        self.adc_data_b_i = Signal(adc_data_width)

        # CD: tdc_dclk_a
        self.tdc_data_a_i = Signal(tdc_data_width)
        self.tdc_data_valid_a_i = Signal()
        # CD: tdc_dclk_b
        self.tdc_data_b_i = Signal(tdc_data_width)
        self.tdc_data_valid_b_i = Signal()

        # CD: sys
        self.source_tagged_integral_a = None
        self.source_tagged_adc_samples_a = None
        self.source_tagged_tdc_samples_a = None
        self.source_tagged_integral_b = None
        self.source_tagged_adc_samples_b = None
        self.source_tagged_tdc_samples_b = None

        # # #

        triggers = Signal(2)

        for idx, ch in enumerate(["a", "b"]):
            mcord_daq_channel = MCORDDAQChannel(
                trigger_id_width=trigger_id_width,
                adc_data_width=adc_data_width,
                tdc_data_width=tdc_data_width,
                circular_buffer_depth=circular_buffer_depth,
                throttler_max_acquisitions=throttler_max_acquisitions
            )
            self.submodules += ClockDomainsRenamer({
                "adc_dclk": f"adc_dclk_{ch}",
                "tdc_dclk": f"tdc_dclk_{ch}"
            })(mcord_daq_channel)
            self.comb += [
                mcord_daq_channel.trigger_i.eq(self.trigger_i),
                mcord_daq_channel.trigger_id_i.eq(self.trigger_id_i),
                mcord_daq_channel.pretrigger_i.eq(self.pretrigger_i),
                mcord_daq_channel.pposttrigger_i.eq(self.pposttrigger_i),
                mcord_daq_channel.throttler_acq_num_i.eq(self.throttler_acq_num_i),
                mcord_daq_channel.throttler_acq_len_i.eq(self.throttler_acq_len_i),
                mcord_daq_channel.throttler_arm_i.eq(self.throttler_arm_i),
                mcord_daq_channel.throttler_rst_i.eq(self.throttler_rst_i),
                mcord_daq_channel.trigger_mode_i.eq(self.trigger_mode_i),
                mcord_daq_channel.trigger_level_i.eq(self.trigger_level_i),
                triggers[idx].eq(mcord_daq_channel.trigger_o)
            ]
            setattr(self, f"source_tagged_integral_{ch}", mcord_daq_channel.source_tagged_integral)
            setattr(self, f"source_tagged_adc_samples_{ch}", mcord_daq_channel.source_tagged_adc_samples)
            setattr(self, f"source_tagged_tdc_samples_{ch}", mcord_daq_channel.source_tagged_tdc_samples)

        coincidence_detector = CoincidenceDetector(2, detection_window_max_length=255)
        self.submodules += coincidence_detector
        self.comb += [
            coincidence_detector.trigger_i.eq(triggers),
            coincidence_detector.enabled_i.eq(1),
            coincidence_detector.mask_i.eq(0b11),
            coincidence_detector.detection_window_i.eq(self.coincidence_detection_window_i),
            self.trigger_o.eq(coincidence_detector.trigger_o)
        ]
        
        self.sync += [
            If(self.event_counter_enabled_i,
                If(self.trigger_o,
                    self.event_counter_o.eq(self.event_counter_o+1))
            ).Else(
                self.event_counter_o.eq(0)
            )
        ]
