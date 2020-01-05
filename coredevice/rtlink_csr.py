from artiq.language.core import kernel, delay, portable
from artiq.language.units import ns
from artiq.coredevice.rtio import rtio_output, rtio_input_data
from artiq.language.types import TInt32
import csv


class RtlinkCsr:

    class Reg:

        def __init__(self, channel, address, length):
            self.channel = channel
            self.address = address
            self.length = length

        @kernel
        def write(self, data):
            rtio_output((self.channel << 8) | self.address << 1 | 1, data & ((0x1 << self.length)-1))

        @kernel
        def read(self) -> TInt32:
            rtio_output((self.channel << 8) | self.address << 1 | 0, 0)
            return rtio_input_data(self.channel)

    def __init__(self, dmgr, channel, config=None, config_file=None, core_device="core"):
        self.channel = channel
        self.core = dmgr.get(core_device)
        self.ref_period_mu = self.core.seconds_to_mu(
            self.core.coarse_ref_period)

        if config:
            for reg in config:
                new_reg = RtlinkCsr.Reg(self.channel, reg[0], reg[2])
                setattr(self, reg[1], new_reg)
        elif config_file:
            with open(config_file, 'r') as f:
                reg_reader = csv.reader(f, delimiter=',')
                next(reg_reader)  # ignore header
                for reg in reg_reader:
                    new_reg = RtlinkCsr.Reg(self.channel, reg[0], reg[2])
                    setattr(self, reg[1], new_reg)
        else:
            raise ValueError("Invalid RTLink CSR configuration")
