from migen import *
from migen.genlib.fsm import FSM
from misoc.interconnect.stream import Endpoint


class TriggeredCircularBuffer(Module):

    """Triggered Circular Buffer

    Implementation of circular buffer with triggered readout and configurable
    pretrigger / posttrigger.

    Simple, single clock-domain implementation.

    If pretrigger and posttrigger are 0 there is only one sample at the trigger re.
    
    Pretrigger <= depth-2
    Posttrigger <= depth-1
    pretrigger+posttrigger <= depth-1

    Due to simplified address counter depth must be a power of 2.
    """
    
    def __init__(self, data_width, depth=512):
        # Input interface
        self.data_i = Signal(data_width)
        self.trigger_i = Signal()
        self.pretrigger_i = Signal(max=depth-1)
        self.posttrigger_i = Signal(max=depth-1)  
        # Output interface
        self.source = Endpoint([("data", data_width)])

        # # #

        assert 2**len(Signal(max=depth)) == depth

        buffer = Memory(data_width, depth)
        wr_port = buffer.get_port(write_capable=True)
        rd_port = buffer.get_port(has_re=True)
        self.specials += [buffer, wr_port, rd_port]
        
        self.wr_ptr = wr_ptr = Signal.like(wr_port.adr)
        self.rd_ptr = rd_ptr = Signal.like(rd_port.adr)

        # We need more than depth to accommodate 0/0 case
        readout_cnt = Signal(max=depth+1)
        readout_fsm = FSM("IDLE")
        self.submodules += readout_fsm

        trigger_d = Signal()
        self.sync += trigger_d.eq(self.trigger_i)

        readout_fsm.act("IDLE",
            rd_port.re.eq(0),
            NextValue(self.source.stb, 0),
            If(self.trigger_i & ~trigger_d, 
                NextState("READOUT"),
                NextValue(readout_cnt, self.pretrigger_i+self.posttrigger_i+1),
            )
        )
        readout_fsm.act("READOUT",
            rd_port.re.eq(1),
            If(readout_cnt != 0, 
                NextValue(readout_cnt, readout_cnt-1),
                NextValue(self.source.stb, 1),
            ).Else(
                NextState("IDLE"),
                NextValue(self.source.stb, 0),
            )
        )

        self.comb += [
            wr_port.we.eq(1),
            wr_port.adr.eq(wr_ptr),
            wr_port.dat_w.eq(self.data_i),
            rd_port.adr.eq(rd_ptr),
            self.source.payload.data.eq(rd_port.dat_r)
        ]
        # TODO: Implement more complex address counters so that depths other than 
        #       power of 2 are allowed.
        self.sync += [
            self.source.eop.eq(readout_cnt == 1),
            rd_ptr.eq(wr_ptr-self.pretrigger_i),
            wr_ptr.eq(wr_ptr+1),
        ]


if __name__ == "__main__":
    from elhep_cores.simulation.common import generate_verilog
    dut = TriggeredCircularBuffer(16, depth=128)
    generate_verilog(dut, "dut.v")