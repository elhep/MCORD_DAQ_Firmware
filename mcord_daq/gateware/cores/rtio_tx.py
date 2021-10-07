import os

from migen import *
from artiq.gateware.rtio import rtlink
from artiq.gateware.rtio.channel import Channel
from elhep_cores.helpers.ddb_manager import HasDdbManager


class RTIOTxChannel(Module):

    def __init__(self, data_width, timestamped=False):
        self.data_i = Signal(data_width)
        self.data_valid_i = Signal()

        # # #

        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=0, address_width=0, fine_ts_width=False),
            rtlink.IInterface(data_width=data_width, timestamped=timestamped)
        )
        self.comb += [
            self.rtlink.i.data.eq(self.data_i),
            self.rtlink.i.stb.eq(self.data_valid_i)
        ]


class RTIOTx(Module, HasDdbManager):

    def __init__(self, channels, ddb_identifier="rtiotx"):
        for idx, channel in enumerate(channels):
            phy = RTIOTxChannel(data_width=len(channel['data']), timestamped=channel['timestamped'])
            self.submodules += phy
            self.comb += [
                phy.data_i.eq(channel['data']),
                phy.data_valid_i.eq(channel['data_valid']),
            ]
            self.add_rtio_channels(
                channel=Channel.from_phy(phy),
                device_id=f"{ddb_identifier}_ch{idx}",
                module="mcord_daq.coredevice.rtiotx",
                class_name="RTIOTx",
                arguments={"width": len(channel['data']), "timestamped": channel['timestamped']}
            )
