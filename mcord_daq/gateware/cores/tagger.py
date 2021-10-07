from migen import *
from migen.genlib.fifo import SyncFIFO
from migen.genlib.fsm import FSM
from misoc.interconnect.stream import Endpoint


class Tagger(Module):

    def __init__(self, data_width, tag_id_width):
        self.sink = Endpoint([("data", data_width)])
        self.source = Endpoint([("data", data_width+tag_id_width)])
        self.tag_i = Signal(tag_id_width)
        self.tag_valid_i = Signal()

        # # #

        current_tag = Signal.like(self.tag_i)
        ivalid_tag = Replicate(1, len(current_tag))
        sink_data_d1 = Signal.like(self.sink.payload.data)
        sink_data_d2 = Signal.like(self.sink.payload.data)
        sink_stb_d1 = Signal()
        sink_stb_d2 = Signal()
        sink_eop_d1 = Signal()
        sink_eop_d2 = Signal()
        self.sync += [
            sink_data_d2.eq(sink_data_d1),
            sink_data_d1.eq(self.sink.payload.data),
            sink_stb_d2.eq(sink_stb_d1),
            sink_stb_d1.eq(self.sink.stb),
            sink_eop_d2.eq(sink_eop_d1),
            sink_eop_d1.eq(self.sink.eop)
        ]

        fifo = SyncFIFO(tag_id_width, 2)
        self.submodules += fifo
        self.comb += [
            fifo.din.eq(self.tag_i),
            fifo.we.eq(fifo.writable & self.tag_valid_i)
        ]

        fsm = FSM("IDLE")
        self.submodules += fsm

        fsm.act("IDLE",
            NextValue(current_tag, ivalid_tag),
            If(fifo.readable,
                NextValue(fifo.re, 1),
                NextState("GET_TAG"),
            )
        )
        fsm.act("GET_TAG",
            NextValue(fifo.re, 0),
            NextValue(current_tag, fifo.dout),
            NextState("VALID_TAG")
        )
        fsm.act("VALID_TAG",
            If(sink_eop_d1 & fifo.readable, NextState("GET_TAG")),
            If(sink_eop_d1, NextState("IDLE"))
        )

        self.comb += [
            self.source.payload.data.eq(Cat(sink_data_d2, current_tag)),
            self.source.stb.eq(sink_stb_d2),
            self.source.eop.eq(sink_eop_d2)
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import generate_verilog
    dut = Tagger(16, 16)
    generate_verilog(dut, "dut.v")
        