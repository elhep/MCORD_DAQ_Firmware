import os

from migen import *
from misoc.interconnect.stream import Endpoint
from artiq.gateware.rtio import rtlink
from artiq.gateware.rtio.channel import Channel
from elhep_cores.helpers.ddb_manager import HasDdbManager


class RtioTx(Module, HasDdbManager):

    def __init__(self, sink, identifier, timestamped=False):
        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=0, address_width=0, fine_ts_width=False),
            rtlink.IInterface(data_width=len(sink.payload.data), timestamped=timestamped)
        )
        self.comb += [
            self.rtlink.i.data.eq(sink.payload.data),
            self.rtlink.i.stb.eq(sink.stb)
        ]
        
        self.add_rtio_channels(
            channel=Channel.from_phy(phy),
            device_id=identifier,
            module="mcord_daq.coredevice.rtio_tx",
            class_name="RtioTx",
            arguments={
                "width": len(sink.payload.data), 
                "timestamped": timestamped
            }
        )
