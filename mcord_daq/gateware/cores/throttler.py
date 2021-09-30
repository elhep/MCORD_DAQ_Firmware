from migen import *

from migen.genlib.fsm import FSM


class Throttler(Module):

    def __init__(self, data_width, max_acquisitions=16, max_acquisition_len=1024):
        self.data_i = Signal(data_width)
        self.data_valid_i = Signal()
        self.data_o = Signal(data_width)
        self.data_valid_o = Signal()

        self.arm_i = Signal()
        self.rst_i = Signal()
        self.acq_num_i = Signal(max=max_acquisitions)
        self.acq_len_i = Signal(max=max_acquisition_len)

        # # #

        acquisition_counter = Signal(max=max_acquisitions)
        acquisition_sample_counter = Signal(max=max_acquisition_len)
        arm_d = Signal()
        self.sync += arm_d.eq(self.arm_i)
        data_valid_d = Signal()
        self.sync += data_valid_d.eq(self.data_valid_i)
        acq_num_d = Signal.like(self.acq_num_i)
        acq_len_d = Signal.like(self.acq_len_i)

        fsm = FSM("IDLE")
        self.submodules += fsm

        fsm.act("IDLE",
            If(~arm_d & self.arm_i & self.acq_num_i > 0,
                NextState("ARM"),
                NextValue(acquisition_counter, self.acq_num_i),
                NextValue(acq_len_d, self.acq_len_i),
            )
        )
        fsm.act("ARM",
            If(~data_valid_d & self.data_valid_i,
                NextValue(acquisition_counter, acquisition_counter-1),
                NextValue(acquisition_sample_counter, acq_len_d),
                NextState("ACQ"),
            ),
            If(self.rst_i, NextState("IDLE"))
        )
        fsm.act("ACQ",
            If(acquisition_sample_counter == 0,
                If(acquisition_counter == 0, NextState("IDLE"))
                .Else(NextState("ARM"))
            ).Else(
                NextValue(acquisition_sample_counter, acquisition_sample_counter-1)
            ),
            If(self.rst_i, NextState("IDLE"))
        )

        data_i_d = Signal.like(self.data_i)
        self.sync += [
            data_i_d.eq(self.data_i),
            self.data_o.eq(data_i_d),
            self.data_valid_o.eq(data_valid_d & fsm.ongoing("ACQ"))
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import generate_verilog
    dut = Throttler(16, max_acquisitions=16, max_acquisition_len=1024)
    generate_verilog(dut, "dut.v")
        