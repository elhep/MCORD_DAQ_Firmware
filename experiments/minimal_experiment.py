from artiq.experiment import *
from artiq.language.units import ns, us
from artiq.coredevice.rtio import rtio_output, rtio_input_data
from artiq.language.types import TInt32


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")

        self.channel = 0

    @kernel
    def write(self, address, data):
        rtio_output((self.channel << 8) | address << 1 | 1, data)

    @kernel
    def read(self, address) -> TInt32:
        rtio_output((self.channel << 8) | address << 1 | 0, 0)
        return rtio_input_data(self.channel)

    @kernel
    def run(self):
        self.core.break_realtime()
        # self.write
        # self.read
        # ...
