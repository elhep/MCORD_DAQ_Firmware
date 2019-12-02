from artiq.gateware.fmc import _FMC, _fmc_pin
from migen.build.generic_platform import *

from artiq.gateware.rtio.phy.ttl_simple import *
from artiq.gateware.rtio.phy.spi2 import SPIMaster

from misoc.cores import gpio
from artiq.gateware import rtio


class FmcAdc100M10b16chaTdc(_FMC):

    @classmethod
    def signal_name(cls, signal_name, fmc):
        return (cls.__name__ + "{}_{}").format(fmc, signal_name)

    @classmethod
    def diff_signal(cls, signal_name, fmc, bank, i, iostd_diff, idx=0):
        return (cls.signal_name(signal_name, fmc), idx,
                Subsignal("p", Pins(_fmc_pin(fmc, bank, i, "p"))),
                Subsignal("n", Pins(_fmc_pin(fmc, bank, i, "n"))),
                IOStandard(iostd_diff[bank]))

    @classmethod
    def single_signal(cls, signal_name, fmc, bank, i, pol, iostd_single, idx=0):
        return (cls.signal_name(signal_name, fmc), idx, _fmc_pin(fmc, bank, i, pol), IOStandard(iostd_single[bank])),

    @classmethod
    def io(cls, fmc, iostd_single, iostd_diff):
        return [
            cls.diff_signal("trig", fmc, "HB", 12, iostd_diff),
            cls.diff_signal("idx_in", fmc, "LA", 32, iostd_diff),

            cls.diff_signal("adc_out_adclk", fmc, "HB", 0, iostd_diff, idx=0),
            cls.diff_signal("adc_out_lclk", fmc, "HB", 6, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out0", fmc, "HB", 2, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out1", fmc, "HB", 9, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out2", fmc, "HB", 8, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out3", fmc, "HB", 3, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out4", fmc, "HB", 5, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out5", fmc, "HB", 7, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out6", fmc, "HB", 4, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out7", fmc, "HB", 1, iostd_diff, idx=0),

            cls.diff_signal("adc_out_adclk", fmc, "HA", 17, iostd_diff, idx=1),
            cls.diff_signal("adc_out_lclk", fmc, "HA", 1, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out0", fmc, "HA", 10, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out1", fmc, "HA", 15, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out2", fmc, "HA", 18, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out3", fmc, "HA", 14, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out4", fmc, "HA", 16, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out5", fmc, "HA", 12, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out6", fmc, "HA", 11, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out7", fmc, "HA", 13, iostd_diff, idx=1),

            cls.diff_signal("tdc_out_lclkout", fmc, "HB", 17, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame0", fmc, "HB", 20, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo0", fmc, "HB", 13, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame1", fmc, "HB", 15, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo1", fmc, "HB", 19, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame2", fmc, "HB", 21, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo2", fmc, "HB", 16, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame3", fmc, "HB", 14, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo3", fmc, "HB", 18, iostd_diff, idx=0),

            cls.diff_signal("tdc_out_lclkout", fmc, "LA", 17, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame0", fmc, "LA", 24, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo0", fmc, "LA", 25, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame1", fmc, "LA", 26, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo1", fmc, "LA", 21, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame2", fmc, "LA", 22, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo2", fmc, "LA", 23, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame3", fmc, "LA", 19, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo3", fmc, "LA", 20, iostd_diff, idx=1),

            cls.diff_signal("tdc_out_lclkout", fmc, "LA", 0, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame0", fmc, "LA", 9, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo0", fmc, "LA", 7, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame1", fmc, "LA", 8, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo1", fmc, "LA", 5, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame2", fmc, "LA", 6, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo2", fmc, "LA", 5, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame3", fmc, "LA", 3, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo3", fmc, "LA", 2, iostd_diff, idx=2),

            cls.diff_signal("tdc_out_lclkout", fmc, "HA", 0, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame0", fmc, "HA", 2, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo0", fmc, "HA", 3, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame1", fmc, "HA", 7, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo1", fmc, "HA", 8, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame2", fmc, "HA", 6, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo2", fmc, "HA", 4, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame3", fmc, "HA", 5, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo3", fmc, "HA", 9, iostd_diff, idx=3),

            cls.diff_signal("tdc_dis", fmc, "HB", 10, iostd_diff, idx=0),
            cls.diff_signal("tdc_dis", fmc, "HA", 23, iostd_diff, idx=1),
            cls.diff_signal("tdc_dis", fmc, "LA", 1, iostd_diff, idx=2),
            cls.diff_signal("tdc_dis", fmc, "LA", 10, iostd_diff, idx=3),

            (cls.signal_name("adc_spi", fmc), 0,
             Subsignal("sck", Pins(_fmc_pin(fmc, "HA", 22, "p")), IOStandard(iostd_single["HA"])),
             Subsignal("miso", Pins(_fmc_pin(fmc, "HA", 21, "n")), IOStandard(iostd_single["HA"])),
             Subsignal("mosi", Pins(_fmc_pin(fmc, "LA", 16, "p")), IOStandard(iostd_single["LA"])),
             ),
            cls.single_signal("adc_spi_csn", fmc, "HA", 22, "n", iostd_single, idx=0),
            cls.single_signal("adc_spi_csn", fmc, "LA", 11, "n", iostd_single, idx=1),

            cls.single_signal("adc_resetn", fmc, "LA", 15, "p", iostd_single, idx=0),
            cls.single_signal("adc_sync", fmc, "LA", 30, "p", iostd_single, idx=0),

            (cls.signal_name("tdc_spi", fmc), 0,
             Subsignal("sck", Pins(_fmc_pin(fmc, "LA", 15, "n")), IOStandard(iostd_single["LA"])),
             Subsignal("miso", Pins(_fmc_pin(fmc, "LA", 16, "n")), IOStandard(iostd_single["LA"])),
             Subsignal("mosi", Pins(_fmc_pin(fmc, "LA", 13, "p")), IOStandard(iostd_single["LA"])),
             ),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 31, "n", iostd_single, idx=0),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 31, "p", iostd_single, idx=1),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 12, "p", iostd_single, idx=2),
            cls.single_signal("tdc_spi_csn", fmc, "HA", 20, "n", iostd_single, idx=3),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 14, "n", iostd_single, idx=4),  # CLK CSN

            # TDC INT and TDC PAR are not supported

            cls.single_signal("trig_term", fmc, "LA", 14, "p", iostd_single, idx=0),
            cls.single_signal("trig_dir", fmc, "LA", 13, "n", iostd_single, idx=0),
            cls.single_signal("ref_sel", fmc, "LA", 29, "p", iostd_single, idx=0),
            cls.single_signal("idx_src_sel", fmc, "LA", 30, "n", iostd_single, idx=0),

            # PGOOD is not supported
            # cls.single_signal("pgood", fmc, "LA", 29, "n", iostd_single, idx=0),

            (cls.signal_name("dac_i2c", fmc), 0,
             Subsignal("scl", Pins(_fmc_pin(fmc, "LA", 27, "n")), IOStandard(iostd_single["LA"])),
             Subsignal("sda", Pins(_fmc_pin(fmc, "LA", 27, "p")), IOStandard(iostd_single["LA"])),
             ),

            cls.single_signal("tp35", fmc, "LA", 18, "p", iostd_single, idx=0),
            cls.single_signal("tp36", fmc, "LA", 18, "n", iostd_single, idx=0),
            cls.single_signal("tp37", fmc, "HA", 20, "p", iostd_single, idx=0),
            cls.single_signal("tp38", fmc, "HA", 21, "p", iostd_single, idx=0),
            cls.single_signal("tp39", fmc, "HB", 11, "p", iostd_single, idx=0),
            cls.single_signal("tp40", fmc, "HB", 11, "n", iostd_single, idx=0),
        ]

    @classmethod
    def add_std(cls, target, fmc, iostd_single, iostd_diff):
        cls.add_extension(target, fmc, iostd_single, iostd_diff)

        dac_i2c = target.platform.request(cls.signal_name("dac_i2c", fmc))
        target.submodules.i2c = gpio.GPIOTristate([dac_i2c.scl, dac_i2c.sda])
        target.csr_devices.append("i2c")

        # This will require external buffer definition
        # pads = target.platform.request(cls.signal_name("trig", fmc))
        # phy = InOut(pads.p, pads.n)
        # target.submodules += phy
        # target.rtio_channels.append(rtio.Channel.from_phy(phy, ififo_depth=4))
        #

        for i in range(4):
            pads = target.platform.request(cls.signal_name("tdc_dis", fmc), i)
            phy = Output(pads.p, pads.n)
            target.submodules += phy
            target.rtio_channels.append(rtio.Channel.from_phy(phy))

        for sn in ["idx_in", "adc_resetn", "adc_sync", "trig_term", "trig_dir", "ref_sel", "idx_src_sel"]:
            pads = target.platform.request(cls.signal_name(sn, fmc))
            if hasattr(pads, "p"):
                phy = Output(pads.p, pads.n)
            else:
                phy = Output(pads)
            target.submodules += phy
            target.rtio_channels.append(rtio.Channel.from_phy(phy))
