from artiq.experiment import *


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")

    @kernel
    def run(self):
        self.core.break_realtime()
        self.fmc1.adc_resetn.off()
        delay(1 * ms)
        self.fmc1.adc_resetn.on()
        delay(1 * ms)
        self.fmc1.clock.write(0x0, 0b00011000)
        self.fmc1.clock.write(0xf, 1)
        delay(1*ms)
        while True:
            for i in range(0x3, 0xF):
                self.core.break_realtime()
                vid0 = self.fmc1.clock.read(0xc)
                print(i, vid0)