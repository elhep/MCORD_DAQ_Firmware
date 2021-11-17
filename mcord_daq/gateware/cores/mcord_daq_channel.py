from migen import *
from misoc.interconnect.stream import AsyncFIFO

from mcord_daq.gateware.cores.circular_buffer import TriggeredCircularBuffer
from mcord_daq.gateware.cores.throttler import Throttler
from mcord_daq.gateware.cores.tagger import Tagger
from mcord_daq.gateware.cores.integral import Integral
from mcord_daq.gateware.cores.tdc_sample_selector import TdcSampleSelector
from mcord_daq.gateware.cores.channel_trigger_generator import ChannelTriggerGenerator
from mcord_daq.gateware.cores.baseline_generator import BaselineGenerator
from mcord_daq.gateware.cores.common import cdc


class MCORDDAQChannel(Module):

    def __init__(self, trigger_id_width, adc_data_width, tdc_data_width, circular_buffer_depth,
                 throttler_max_acquisitions):
        # CD: sys
        self.trigger_i = Signal()
        self.trigger_id_i = Signal(trigger_id_width)
        self.pretrigger_i = Signal(max=circular_buffer_depth)
        self.pposttrigger_i = Signal(max=circular_buffer_depth)
        self.throttler_acq_num_i = Signal(max=throttler_max_acquisitions)
        self.throttler_acq_len_i = Signal(max=circular_buffer_depth)
        self.throttler_arm_i = Signal()
        self.throttler_rst_i = Signal()

        self.trigger_mode_i = Signal(11)
        self.trigger_level_i = Signal(adc_data_width)

        # CD: adc_dclk
        self.adc_data_i = Signal(adc_data_width)

        # CD: tdc_dclk
        self.tdc_data_i = Signal(tdc_data_width)
        self.tdc_data_valid_i = Signal()

        # CD: sys
        self.source_tagged_integral = None
        self.source_tagged_adc_samples = None
        self.source_tagged_tdc_samples = None

        # CD: sys
        self.trigger_o = Signal()

        # # #

        # ADC Path

        adc_circular_buffer = TriggeredCircularBuffer(data_width=adc_data_width, depth=circular_buffer_depth)
        self.submodules += ClockDomainsRenamer("adc_dclk")(adc_circular_buffer)
        self.comb += [
            adc_circular_buffer.data_i.eq(self.adc_data_i),
            adc_circular_buffer.trigger_i.eq(cdc(self, self.trigger_i, "sys", "adc_dclk")),
            adc_circular_buffer.pretrigger_i.eq(cdc(self, self.pretrigger_i, "sys", "adc_dclk")),
            adc_circular_buffer.posttrigger_i.eq(cdc(self, self.pposttrigger_i, "sys", "adc_dclk")),
        ]
        # As f_rio > f_adc_dclk we can use a small FIFO
        adc_fifo = AsyncFIFO([("data", adc_data_width)], 4)
        self.submodules += ClockDomainsRenamer({"write": "adc_dclk", "read": "sys"})(adc_fifo)
        adc_circular_buffer.source.connect(adc_fifo.sink)

        throttler = Throttler(data_width=adc_data_width, max_acquisitions=throttler_max_acquisitions,
                              max_acquisition_len=circular_buffer_depth)
        self.submodules += throttler
        self.comb += [
            throttler.arm_i.eq(self.throttler_arm_i),
            throttler.rst_i.eq(self.throttler_rst_i),
            throttler.acq_num_i.eq(self.throttler_acq_num_i),
            throttler.acq_len_i.eq(self.throttler_acq_len_i)
        ]
        adc_fifo.source.connect(throttler.sink)

        throttler_tagger = Tagger(data_width=adc_data_width, tag_id_width=trigger_id_width)
        self.submodules += throttler_tagger
        throttler.source.connect(throttler_tagger.sink)
        self.source_tagged_adc_samples = throttler_tagger.source

        integral = Integral(data_width=adc_data_width, max_samples=circular_buffer_depth)
        self.submodules += integral
        adc_fifo.source.connect(integral.sink)

        integral_tagger = Tagger(data_width=len(integral.source.payload.data), tag_id_width=trigger_id_width)
        self.submodules += integral_tagger
        integral.source.connect(integral_tagger.sink)
        self.source_tagged_integral = integral_tagger.source

        # TDC Path

        # MSb of data passed to the circular buffer is data valid.
        tdc_cb_data = Signal(tdc_data_width+1)
        self.comb += tdc_cb_data.eq(Cat(self.tdc_data_valid_i, self.tdc_data_i))
        tdc_circular_buffer = TriggeredCircularBuffer(data_width=tdc_data_width+1, depth=circular_buffer_depth)
        self.submodules += ClockDomainsRenamer("tdc_dclk")(tdc_circular_buffer)
        self.comb += [
            tdc_circular_buffer.data_i.eq(tdc_cb_data),
            tdc_circular_buffer.trigger_i.eq(cdc(self, self.trigger_i, "sys", "tdc_dclk")),
            tdc_circular_buffer.pretrigger_i.eq(cdc(self, self.pretrigger_i, "sys", "tdc_dclk")),
            tdc_circular_buffer.posttrigger_i.eq(cdc(self, self.pposttrigger_i, "sys", "tdc_dclk")),
        ]

        # As f_rio > f_tdc_dclk we can use a small FIFO
        tdc_fifo = AsyncFIFO([("data", tdc_data_width+1)], 4)
        self.submodules += ClockDomainsRenamer({"write": "tdc_dclk", "read": "sys"})(tdc_fifo)
        tdc_circular_buffer.source.connect(tdc_fifo.sink)

        tdc_tagger = Tagger(data_width=len(tdc_fifo.source.payload.data), tag_id_width=trigger_id_width)
        self.submodules += tdc_tagger
        tdc_fifo.source.connect(tdc_tagger.sink)

        tdc_sample_selector = TdcSampleSelector(data_width=len(tdc_tagger.source.payload.data))
        self.submodules += tdc_sample_selector
        tdc_tagger.source.connect(tdc_sample_selector.sink)
        self.source_tagged_tdc_samples = tdc_sample_selector.source

        # Triggering

        baseline_generator = BaselineGenerator(adc_data_width)
        self.submodules += ClockDomainsRenamer("adc_dclk")(baseline_generator)
        self.comb += baseline_generator.data_i.eq(self.adc_data_i)

        channel_tg = ChannelTriggerGenerator(adc_data_width)
        self.submodules += ClockDomainsRenamer({"dclk": "adc_dclk"})(channel_tg)
        self.comb += [
            channel_tg.data_i.eq(self.adc_data_i),
            channel_tg.baseline_i.eq(baseline_generator.data_o),
            channel_tg.trigger_mode_i.eq(self.trigger_mode_i),
            channel_tg.trigger_level_i.eq(self.trigger_level_i),
            self.trigger_o.eq(channel_tg.trigger_o)
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import *

    class SimulationWrapper(Module):
        def __init__(self):
            self.adc_dclk_i = Signal()
            self.adc_dclk_rst_i = Signal()
            self.tdc_dclk_i = Signal()
            self.tdc_dclk_rst_i = Signal()
            self.clock_domains.cd_adc_dclk = ClockDomain()
            self.clock_domains.cd_tdc_dclk = ClockDomain("tdc_dclk")
            self.submodules.dut = MCORDDAQChannel(
                trigger_id_width=4,
                adc_data_width=10,
                tdc_data_width=22,
                circular_buffer_depth=1024,
                throttler_max_acquisitions=100
            )
            self.comb += [
                self.cd_adc_dclk.clk.eq(self.adc_dclk_i),
                self.cd_tdc_dclk.clk.eq(self.tdc_dclk_i)
            ]

    tb = SimulationWrapper()
    ios = get_ios(tb)
    ios = ios.union(get_stream_signals(tb.dut.source_tagged_integral))
    ios = ios.union(get_stream_signals(tb.dut.source_tagged_adc_samples))
    ios = ios.union(get_stream_signals(tb.dut.source_tagged_tdc_samples))
    ios = ios.union(get_ios(tb.dut))
    generate_verilog(tb, "dut.v", ios)



