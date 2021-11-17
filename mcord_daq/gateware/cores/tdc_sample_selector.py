from migen import *
from misoc.interconnect.stream import Endpoint


class TdcSampleSelector(Module):

    # FIXME: This is dummy implementation ignoring EOP signal!

    def __init__(self, data_width):
        self.sink = Endpoint([("data", data_width)])
        self.source = Endpoint([("data", data_width-1)])

        # # #

        self.comb += [
            self.source.payload.data.eq(self.sink.payload.data[1:]),
            self.source.stb.eq(self.sink.stb & self.sink.payload.data[0]),
            self.source.eop.eq(0)
        ]
