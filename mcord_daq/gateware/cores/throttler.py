from migen import *

from migen.genlib.fsm import FSM
from misoc.interconnect.stream import Endpoint


class Throttler(Module):

    def __init__(self, data_width, max_acquisitions=16, max_acquisition_len=1024):
        self.sink = Endpoint([("data", data_width)])
        self.source = Endpoint([("data", data_width)])

        self.arm_i = Signal()
        self.rst_i = Signal()
        self.acq_num_i = Signal(max=max_acquisitions)
        self.acq_len_i = Signal(max=max_acquisition_len)

        # # #

        acquisition_counter = Signal(max=max_acquisitions)
        acquisition_sample_counter = Signal(max=max_acquisition_len)
        arm_d = Signal()
        stb_d = Signal()
        eop_d = Signal()
        acq_len_d = Signal.like(self.acq_len_i)

        self.sync += [
            arm_d.eq(self.arm_i),
            stb_d.eq(self.sink.stb),
            eop_d.eq(self.sink.eop)
        ]

        fsm = FSM("IDLE")
        self.submodules += fsm
        fsm.act("IDLE",
            If(~arm_d & self.arm_i & (self.acq_num_i > 0),
                NextState("PREARM"),
                NextValue(acquisition_counter, self.acq_num_i),
                NextValue(acq_len_d, self.acq_len_i),
            )
        )
        fsm.act("PREARM",
            If(stb_d & eop_d, NextState("ARM"))
        )
        fsm.act("ARM",
            If(~stb_d & self.sink.stb,
                NextValue(acquisition_counter, acquisition_counter-1),
                NextValue(acquisition_sample_counter, acq_len_d),
                NextState("ACQ"),
            ),
            If(self.rst_i, NextState("IDLE"))
        )
        fsm.act("ACQ",
            If(stb_d,
                # Packet finished before ending ACQ
                If(eop_d,
                   If(acquisition_counter == 0, NextState("IDLE")).Else(NextState("ARM"))
                # Finished counting
                ).Elif(
                    acquisition_sample_counter == 0, NextState("WAIT_EOP")
                ).Else(
                    NextValue(acquisition_sample_counter, acquisition_sample_counter-1)
                )
            ),
            If(self.rst_i, NextState("IDLE"))
        )
        fsm.act("WAIT_EOP",
            If(stb_d & eop_d,
               If(acquisition_counter == 0, NextState("IDLE")).Else(NextState("ARM"))
            )
        )

        self.sync += [
            self.source.payload.data.eq(self.sink.payload.data)
        ]
        self.comb += [
            self.source.stb.eq((acquisition_sample_counter > 0) & stb_d & fsm.ongoing("ACQ")),
            self.source.eop.eq(
                (((acquisition_sample_counter == 1) | eop_d) & fsm.ongoing("ACQ")) & self.source.stb
            )
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import generate_verilog
    dut = Throttler(16, max_acquisitions=16, max_acquisition_len=1024)
    generate_verilog(dut, "dut.v")
        