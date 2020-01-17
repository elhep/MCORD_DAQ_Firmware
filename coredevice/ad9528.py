import re

from artiq.coredevice import spi2 as spi
from artiq.language.core import kernel

SPI_CONFIG = (0*spi.SPI_OFFLINE | 0*spi.SPI_END |
              0*spi.SPI_INPUT | 1*spi.SPI_CS_POLARITY |
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
        self.chip_select = chip_select

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
    def reset(self):
        self.core.break_realtime()
        self.write(0, 0b10011001)
        self.write(0xF, 1)

    def initialize(self):
        self.reset()
        skip = [0, 1]
        for r in self.regs:
            if r[0] in skip:
                continue
            self.write(r[0], r[1])

    @kernel
    def write(self, addr, data):
        self.spi.set_config_mu(flags=SPI_CONFIG | spi.SPI_END, length=24, div=self.div, cs=self.chip_select)
        self.spi.write((0 << 15) | ((addr & 0x7F) << 16) | (data & 0xFFFF))

    @kernel
    def read(self, addr):
        self.spi.set_config_mu(flags=SPI_CONFIG, length=16, div=self.div, cs=self.chip_select)
        self.spi.write((1 << 15) | (addr & 0x7F))
        self.spi.set_config_mu(SPI_CONFIG | spi.SPI_INPUT | spi.SPI_END, 8, self.div, self.chip_select)
        self.spi.write(0)
        return self.spi.read()
