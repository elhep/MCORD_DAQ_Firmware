import re

from artiq.coredevice import spi2 as spi
from artiq.coredevice.ttl import TTLOut
from artiq.language.core import kernel
from artiq.language.units import *


SPI_CONFIG = (0*spi.SPI_OFFLINE | 0*spi.SPI_END |
              0*spi.SPI_INPUT | 0*spi.SPI_CS_POLARITY |
              0*spi.SPI_CLK_POLARITY | 0*spi.SPI_CLK_PHASE |
              0*spi.SPI_LSB_FIRST | 0*spi.SPI_HALF_DUPLEX)


class AD9528:

    def __init__(self, dmgr, spi_device, chip_select, spi_freq=10_000_000, config=None, core_device="core"):
        self.core = dmgr.get(core_device)
        self.ref_period_mu = self.core.seconds_to_mu(
            self.core.coarse_ref_period)

        if isinstance(spi_device, str):
            self.spi = dmgr.get(spi_device)
        else:
            self.spi = spi_device  # type: spi.SPIMaster

        if isinstance(chip_select, TTLOut):
            self.chip_select = 0
            self.csn_device = chip_select
        else:
            self.chip_select = chip_select
            self.csn_device = None

        self.div = self.spi.frequency_to_div(spi_freq)

        self.regs = []
        if config:
            self._parse_config_string(config)

    def _parse_config_string(self, r):
        r = r[0].strip()
        r = r.split('\n')

        self.regs = []
        for rr in r[1:]:
            self.regs.append([int(x.strip(), 16) for x in rr.split(',')[:-1]])

    @kernel
    def config_interface(self):
        self.core.break_realtime()
        self.write(0, 0b00011000)
        delay(1*us)
        # self.write(0xF, 1)
        delay(1 * us)

    def initialize(self):
        self.reset()
        skip = [0, 1]
        for r in self.regs:
            if r[0] in skip:
                continue
            self.write(r[0], r[1])

    @kernel
    def write(self, addr, data):
        cs = self.chip_select
        if self.chip_select == 0:
            self.csn_device.off()
            delay(40*ns)
            cs = 1

        self.spi.set_config_mu(flags=SPI_CONFIG | spi.SPI_END, length=24, div=self.div, cs=cs)
        self.spi.write(((0 << 15) | ((addr & 0x7FFF) << 8) | (data & 0xFF)) << 8)

        if self.chip_select == 0:
            self.csn_device.on()

    @kernel
    def read(self, addr):
        cs = self.chip_select
        if self.chip_select == 0:
            self.csn_device.off()
            delay(40 * ns)
            cs = 1

        self.spi.set_config_mu(flags=SPI_CONFIG, length=16, div=self.div, cs=cs)
        self.spi.write(((1 << 15) | (addr & 0x7FFF)) << 16)

        self.spi.set_config_mu(flags=SPI_CONFIG | spi.SPI_INPUT | spi.SPI_END, length=8, div=self.div, cs=cs)
        self.spi.write(0)

        if self.chip_select == 0:
            self.csn_device.on()

        return self.spi.read()
