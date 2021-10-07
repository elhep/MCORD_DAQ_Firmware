from migen import *
from misoc.interconnect.stream import AsyncFIFO

from mcord_daq.gateware.cores.circular_buffer import TriggeredCircularBuffer
from mcord_daq.gateware.cores.throttler import Throttler
from mcord_daq.gateware.cores.tagger import Tagger
from mcord_daq.gateware.cores.integral import Integral


class MCORDChannel(Module):

    def __init__(self, trigger_id_width, adc_data_width, tdc_data_width, circular_buffer_depth,
                 throttler_max_acquisitions):
        self.trigger_i = Signal()
        self.trigger_id_i = Signal(trigger_id_width)

        self.adc_data_i = None

        self.throttler_num_i = None
        self.throttler_arm_i = None
        self.throttler_rst_i = None

        self.tdc_data_i = None
        self.tdc_data_valid_i = None

        self.baseline_i = None
        self.pretrigger_i = Signal(max=circular_buffer_depth)
        self.pposttrigger_i = Signal(max=circular_buffer_depth)

        self.integral_o = None
        self.integral_valid_o = None

        self.adc_data_o = None
        self.adc_data_valid_o = None

        self.tdc_data_o = None
        self.tdc_data_valid_o = None

        # # #

        adc_circular_buffer = TriggeredCircularBuffer(data_width=adc_data_width,
                                                      depth=circular_buffer_depth)
        # TODO: As f_rio > f_adc_dclk we can use a small FIFO depth
        adc_fifo = ClockDomainsRenamer({"write": "adc_dclk", "read": "rio"})(
            AsyncFIFO(adc_data_width, circular_buffer_depth))
        adc_circular_buffer.source.connect(adc_fifo.sink)



        self.adc_data_i = adc_circular_buffer.data_i
        self.comb += [
            adc_circular_buffer.trigger_i.eq(self.trigger_i),
            adc_circular_buffer.pretrigger_i.eq(self.pretrigger_i),
        ]

        tdc_circular_buffer = TriggeredCircularBuffer(data_width=tdc_data_width,
                                                      depth=circular_buffer_depth)
        self.
        self.comb += [
            adc_circular_buffer.trigger_i.eq(self.trigger_i),
            tdc_circular_buffer.trigger_i.eq(self.trigger_i),
            adc_circular_buffer.pretrigger_i.eq(self.pretrigger_i),
            tdc_circular_buffer.posttrigger_i.eq(self.pposttrigger_i)
        ]

        throttler = Throttler(data_width=adc_data_width, max_acquisitions=throttler_max_acquisitions,
                              max_acquisition_len=circular_buffer_depth)
        integral_sum_width = len(Signal(max=circular_buffer_depth*(2**adc_data_width-1)))
        integral = Integral(data_width=adc_data_width, sum_width=integral_sum_width)
        integral_tagger = Tagger(data_width=integral_sum_width, tag_id_width=trigger_id_width)
        throttler_tagger = Tagger(data_width=adc_data_width, tag_id_width=trigger_id_width)
        tdc_tagger = Tagger(data_width=tdc_data_width, tag_id_width=trigger_id_width)

        self.submodules += [adc_circular_buffer, tdc_circular_buffer, throttler, integral,
                            integral_tagger, throttler_tagger, tdc_tagger]

        self.integral_o = integral.data_o
        self.integral_valid_o = integral.data_valid_o



