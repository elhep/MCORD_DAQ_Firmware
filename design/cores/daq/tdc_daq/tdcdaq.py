from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *


from migen import *
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer
from migen.genlib.fifo import AsyncFIFO, AsyncFIFOBuffered
from migen.fhdl import verilog
from artiq.gateware.rtio import rtlink, Channel


class TdcDaq(Module):

    """
    This one is simple - put data into FIFO in data clock domain and take in rio_phy domain
    """

    def __init__(self, data_i, stb_i, channel_depth):

        data_width = len(data_i)

        assert data_width < 64

        # Interface - rtlink
        rtlink_iface = rtlink.Interface(
            rtlink.OInterface(data_width=1, address_width=0),
            rtlink.IInterface(data_width=32, timestamped=True))
        self.rtlink_channels = [Channel(rtlink_iface, ififo_depth=channel_depth)]
        if data_width > 32:
            rtlink_iface_aux = rtlink.Interface(
                rtlink.OInterface(data_width=1, address_width=0),
                rtlink.IInterface(data_width=data_width-32, timestamped=True))
            self.rtlink_channels.append(Channel(rtlink_iface_aux, ififo_depth=channel_depth))

        # Clock domains
        # self.clock_domains.cd_dclk = cd_dclk = ClockDomain("data_clock")
        # self.clock_domains.cd_rio_phy = cd_rio_phy = ClockDomain("rio_phy")

        daq_start_rio = Signal()
        daq_start_dclk = Signal()
        daq_stop_rio = Signal()
        daq_stop_dclk = Signal()

        daq_enabled_rio = Signal()
        daq_enabled_dclk = Signal()

        self.submodules.daq_start_ps = daq_start_ps = PulseSynchronizer("rio_phy", "dclk")
        self.comb += [
            daq_start_ps.i.eq(daq_start_rio),
            daq_start_dclk.eq(daq_start_ps.o)
        ]
        self.submodules.daq_stop_ps = daq_stop_ps = PulseSynchronizer("rio_phy", "dclk")
        self.comb += [
            daq_stop_ps.i.eq(daq_stop_rio),
            daq_stop_dclk.eq(daq_stop_ps.o)
        ]

        # rtlink support
        self.sync.rio_phy += [
            daq_stop_rio.eq(0),
            daq_start_rio.eq(0),
            If(rtlink_iface.o.stb,
               If(daq_enabled_rio & ~rtlink_iface.o.data[0], daq_stop_rio.eq(1), daq_enabled_rio.eq(0)).
               Elif(~daq_enabled_rio & rtlink_iface.o.data[0], daq_start_rio.eq(1), daq_enabled_rio.eq(1))
            )
        ]

        self.sync.dclk += [
            If(daq_start_dclk, daq_enabled_dclk.eq(1)).
            Elif(daq_stop_dclk, daq_enabled_dclk.eq(0))
        ]

        # FIFO
        fifo = AsyncFIFO(width=data_width, depth=16)
        self.submodules += ClockDomainsRenamer({"write": "dclk", "read": "rio_phy"})(fifo)

        self.comb += fifo.we.eq(stb_i & daq_enabled_dclk)
        self.comb += fifo.din.eq(data_i)

        self.comb += fifo.re.eq(1)
        self.sync.rio_phy += [
            rtlink_iface.i.stb.eq(0),
            If(fifo.readable,
               rtlink_iface.i.stb.eq(1),
               rtlink_iface.i.data.eq(fifo.dout[:32]))
        ]

        if data_width > 32:
            self.sync.rio_phy += [
                rtlink_iface_aux.i.stb.eq(0),
                If(fifo.readable,
                    rtlink_iface_aux.i.data.eq(fifo.dout[32:]),
                    rtlink_iface_aux.i.stb.eq(1)
                )
            ]


class SimulationWrapper(Module):

    def __init__(self):

        data_width = 44

        self.submodules.dut = dut = TdcDaq(data_width, 1024)

        dut.data_i.name_override = "data_i"
        dut.stb_i.name_override = "data_stb_i"

        dut.rtlink_channels[0].interface.o.stb.name_override = "rtlink_stb_i"
        dut.rtlink_channels[0].interface.o.data.name_override = "rtlink_data_i"

        dut.rtlink_channels[0].interface.i.stb.name_override = "rtlink_stb_o"
        dut.rtlink_channels[0].interface.i.data.name_override = "rtlink_data_o"

        dut.rtlink_channels[1].interface.i.stb.name_override = "rtlink_aux_stb_o"
        dut.rtlink_channels[1].interface.i.data.name_override = "rtlink_aux_data_o"

        self.io = {
            dut.cd_dclk.clk,
            dut.cd_dclk.rst,

            dut.data_i,
            dut.stb_i,

            dut.cd_rio_phy.clk,
            dut.cd_rio_phy.rst,

            dut.rtlink_channels[0].interface.o.stb,
            dut.rtlink_channels[0].interface.o.data,

            dut.rtlink_channels[0].interface.i.stb,
            dut.rtlink_channels[0].interface.i.data,

            dut.rtlink_channels[1].interface.i.stb,
            dut.rtlink_channels[1].interface.i.data,
        }


if __name__ == "__main__":

    from migen.build.xilinx import common
    from design.simulation.common import update_tb

    module = SimulationWrapper()
    so = dict(common.xilinx_special_overrides)
    so.update(common.xilinx_s7_special_overrides)

    verilog.convert(fi=module,
                    name="top",
                    special_overrides=so,
                    ios=module.io,
                    create_clock_domains=False).write('tests/tdc_gpx2_daq.v')
    update_tb('tests/tdc_gpx2_daq.v')
