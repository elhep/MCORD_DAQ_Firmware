from migen import *
from migen.genlib.fifo import SyncFIFO
from migen.genlib.fsm import FSM


class Tagger(Module):

    def __init__(self, data_width, tag_id_width):
        self.data_i = Signal(data_width)
        self.data_valid_i = Signal()
        self.data_o = Signal(data_width+tag_id_width)
        self.data_valid_o = Signal()
        self.tag_i = Signal(tag_id_width)
        self.tag_valid_i = Signal()

        # # #

        data_i_d1 = Signal.like(self.data_i)
        data_i_d2 = Signal.like(self.data_i)
        data_valid_i_d1 = Signal()
        data_valid_i_d2 = Signal()
        self.sync += [
            data_i_d2.eq(data_i_d1),
            data_i_d1.eq(self.data_i),
            data_valid_i_d2.eq(data_valid_i_d1),
            data_valid_i_d1.eq(self.data_valid_i)
        ]

        data_valid_re = Signal()
        data_valid_fe = Signal()
        self.comb += [
            data_valid_re.eq(~data_valid_i_d1 & self.data_valid_i),
            data_valid_fe.eq(data_valid_i_d1 & ~self.data_valid_i),
        ]

        fifo = SyncFIFO(tag_id_width, 2)
        self.submodules += fifo

        current_tag = Signal.like(self.tag_i)

        fsm = FSM("IDLE")
        self.submodules += fsm

        fsm.act("IDLE",
            fifo.re.eq(0),
            If(data_valid_re, 
                NextState("GET_TAG"),
            )
        )

        fsm.act("GET_TAG",
            fifo.re.eq(1),
            If(~self.data_valid_i, NextState("IDLE"))
            .Else(
                If(fifo.readable, NextValue(current_tag, fifo.dout))
                .Else(NextValue(current_tag, Replicate(1, len(self.tag_i)))),
                NextState("TAGGING")
            )
        )

        fsm.act("TAGGING",
            fifo.re.eq(0),
            If(~self.data_valid_i, NextState("IDLE"))
        )

        self.comb += [
            fifo.din.eq(self.tag_i),
            fifo.we.eq(fifo.writable & self.tag_valid_i),
            self.data_o.eq(Cat(current_tag, data_i_d2)),
            self.data_valid_o.eq(data_valid_i_d2)
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import generate_verilog
    dut = Tagger(16, 16)
    generate_verilog(dut, "dut.v")
        