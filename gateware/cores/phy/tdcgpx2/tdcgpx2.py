from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *
from migen.genlib.io import DifferentialInput
from gateware.cores.xilinx import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from artiq.gateware import rtio
from gateware.cores.rtlink_csr import RtLinkCSR


class TdcGpx2Phy(Module):

    def __init__(self, platform, data_clk_i, frame_signals_i, data_signals_i):

        # Outputs
        # ==========================================

        self.data_clk_o = Signal()
        self.data_o = []
        self.data_stb_o = []

        # Design
        # ==========================================

        data_clk_to_bufr = Signal()
        self.clock_domains.cd_dclk = cd_dclk = ClockDomain()  # !!!! Inverted!

        self.specials += DifferentialInput(data_clk_i.p, data_clk_i.n, data_clk_to_bufr)
        self.specials += Instance("BUFG", i_I=~data_clk_to_bufr, o_O=cd_dclk.clk)  # !!!! Inverted!
        platform.add_period_constraint(cd_dclk.clk, 4.)

        self.specials += [AsyncResetSynchronizer(cd_dclk, ResetSignal("sys"))]

        self.rtio_channels = []
        for channel, (frame, data) in enumerate(zip(frame_signals_i, data_signals_i)):
            frame_se = Signal()
            data_se = Signal()
            self.specials += DifferentialInput(frame.p, frame.n, frame_se)
            self.specials += DifferentialInput(data.p, data.n, data_se)

            channel_phy = ClockDomainsRenamer("dclk")(TdcGpx2ChannelPhy(frame_i=frame_se, data_i=data_se))
            setattr(self.submodules, "channel{}".format(channel), channel_phy)
            self.data_o.append(channel_phy.data_o)
            self.data_stb_o.append(channel_phy.stb_o)
            self.rtio_channels.append(rtio.Channel.from_phy(channel_phy.csr))


class TdcGpx2ChannelPhy(Module):

    """
    Single TDC GPX2 channel

    This module runs in clock domain defined by TdcGpx2Phy module.
    """

    def __init__(self, frame_i, data_i, max_frame_length=44):

        # Outputs
        # ==========================================

        self.data_o = Signal(max_frame_length)
        self.stb_o = Signal()

        # RTLink Control Status Registers
        # ==========================================

        regs = [
            ("frame_length", max_frame_length.bit_length()),
            ("frame_delay_value", 5),
            ("data_delay_value", 5)
        ]

        csr = RtLinkCSR(regs, "tdc_gpx_channel_phy")
        self.submodules.csr = csr

        # Design
        # ==========================================

        frame = Signal(2)
        frame_in = Signal()
        self.submodules += ClockDomainsRenamer("rio_phy")(XilinxIdelayE2(
            data_i=frame_i,
            data_o=frame_in,
            delay_value_i=csr.frame_delay_value,
            delay_value_ld_i=csr.frame_delay_value_ld))

        self.sync += [frame.eq(frame << 1 | frame_in)]
        frame_start = Signal()
        self.comb += frame_start.eq(frame[0] & ~frame[1])

        data = Signal()
        self.submodules += ClockDomainsRenamer("rio_phy")(XilinxIdelayE2(
            data_i=data_i,
            data_o=data,
            delay_value_i=csr.data_delay_value,
            delay_value_ld_i=csr.data_delay_value_ld))

        data_q1 = Signal()
        data_q2 = Signal()
        data_q1q2 = Signal(2)
        self.submodules += XilinxDDRInputImplS7(i=data, o1=data_q2, o2=data_q1, clk=ClockSignal(),
                                                clk_edge="SAME_EDGE_PIPELINED")
        self.comb += data_q1q2.eq(Cat(data_q1, data_q2))

        shift_register = Signal(max_frame_length)
        shift_register_reg = Signal.like(shift_register)
        stb_reg = Signal()
        bit_counter = Signal(max=max_frame_length)
        self.submodules.fsm = fsm = FSM(reset_state="IDLE")
        fsm.act("IDLE",
                NextValue(bit_counter, csr.frame_length),
                NextValue(stb_reg, 0),
                If(frame_start,
                   NextState("FRAMEACQ")
                )
        )
        fsm.act("FRAMEACQ",
                NextValue(bit_counter, bit_counter-2),
                NextValue(stb_reg, 0),
                If(bit_counter == 0,
                   NextValue(shift_register_reg, shift_register),
                   NextValue(stb_reg, 1),
                   If(frame_start,
                      NextValue(bit_counter, csr.frame_length)
                   ).Else(
                       NextState("IDLE"))
                )
        )

        self.sync += [
            shift_register.eq((shift_register << 2) | data_q1q2)
        ]

        self.comb += [
            self.data_o.eq(shift_register_reg),
            self.stb_o.eq(stb_reg)
        ]


class SimulationWrapper(Module):

    def __init__(self, platform, max_frame_length):
        self.submodules.dut = dut = TdcGpx2ChannelPhy(max_frame_length=max_frame_length, frame_idelay=False)
        self.submodules += XilinxIdelayctrl(platform.request("ref_clk_200MHz"))
        self.comb += [
            dut.data_clk_i.eq(platform.request("data_clk_i")),
            dut.frame_i.eq(platform.request("frame_i")),
            dut.data_i.eq(platform.request("data_i")),
            dut.frame_length_i.eq(platform.request("frame_length_i")),
            platform.request("data_o").eq(dut.data_o),
            platform.request("stb_o").eq(dut.stb_o)
        ]


class Platform(XilinxPlatform):
    # default_clk_name = "clk"

    def __init__(self, frame_length):
        XilinxPlatform.__init__(self, "xc7", [
            # ("clk", 0, Pins("X")),
            ("data_clk_i", 0, Pins("X")),
            ("ref_clk_200MHz", 0, Pins("X")),
            ("frame_i", 0, Pins("X")),
            ("data_i", 0, Pins("X")),
            ("data_o", 0, Pins(" ".join(["X"]*frame_length))),
            ("stb_o", 0, Pins("X")),
            ("frame_length_i", 0, Pins(" ".join(['X']*6)))
        ])


if __name__ == "__main__":
    # Generate simulation source for Cocotb
    from gateware.simulation.common import generate_cocotb_tb
    platform = Platform(44)
    module = SimulationWrapper(platform, max_frame_length=44)
    generate_cocotb_tb(platform, module)
