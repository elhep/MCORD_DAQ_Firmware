from migen import *

from mcord_daq.gateware.cores.mcord_channel import MCORDChannel
from mcord_daq.gateware.cores.rtio_csr import RTStatus, RTStorage, RTReg
from mcord_daq.gateware.cores.rtio_tx import RtioTx


class MCORDChannelRTIOWrapper(Module):

    def __init__(self, trigger_id_width, adc_data_width, tdc_data_width, 
            circular_buffer_depth, throttler_max_acquisitions, ddb_prefix):
        # CD: rio_phy
        self.trigger_i = Signal()
        self.trigger_id_i = Signal(trigger_id_width)
        self.trigger_o = Signal()
        
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

        # # #

        rio_phy = ClockDomainsRenamer("rio_phy")
        mcord_channel = MCORDChannel(trigger_id_width, adc_data_width, tdc_data_width, 
            circular_buffer_depth, throttler_max_acquisitions)
        self.submodules += rio_phy(mcord_channel)

        # Configuration registers
        fields = [
            RTStorage("pretrigger", mcord_channel.pretrigger_i, 
                description="Pretrigger length"),
            RTStorage("posttrigger", mcord_channel.posttrigger_i, 
                description="Posttrigger length"),
            RTStorage("throttler_acq_num", mcord_channel.throttler_acq_num_i, 
                description="Number of test acquisitions of ADC samples"),
            RTStorage("throttler_acq_len", mcord_channel.throttler_acq_len_i, 
                description="Length of single test ADC acquisition"),
            RTStorage("throttler_arm", mcord_channel.throttler_arm_i, width=0,
                description="Arm test ADC acquisition mechanism"),
            RTStorage("throttler_rst", mcord_channel.throttler_rst_i, width=0,
                description="Reset test ADC acquisition mechanism"),
            RTStorage("trigger_mode", mcord_channel.trigger_mode_i,
                description="Trigger mode"),
            RTStorage("trigger_level", mcord_channel.trigger_level_i,
                description="Trigger level"),
            RTStorage("event_counter_enabled", mcord_channel.event_counter_enabled_i,
                description="Event counter enabled"),
            RTStatus("event_counter", mcord_channel.event_counter_o,
                description="Number of events registered for the channel"),
        ]
        self.submodules += RTReg(fields, f"{ddb_prefix}_rtio_csr")
        
        # Data TX
        sources = [
            "tagged_integral_a", "tagged_integral_b",
            "tagged_adc_samples_a", "tagged_adc_samples_b",
            "tagged_tdc_samples_a", "tagged_tdc_samples_b"
        ]
        for source in sources:
            sink = getattr(mcord_channel, f"source_{source}")
            identifier = f"{ddb_prefix}_rtio_tx_{source}"
            self.submodules += RtioTx(sink, identifier)
