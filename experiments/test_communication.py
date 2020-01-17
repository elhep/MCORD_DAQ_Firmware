from artiq.experiment import *


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")

    @kernel
    def run(self):
        self.core.break_realtime()
        self.fmc1.initialize()



        addr = [0x3, 0x4, 0x5]

        while True:

            self.core.break_realtime()

            self.fmc1.adc_resetn.off()
            delay(1 * ms)
            self.fmc1.adc_resetn.on()
            delay(1 * ms)

            self.fmc1.clock.config_interface()
            self.fmc1.clock.write(0xF, 1)


            for a in addr:
                self.core.break_realtime()
                print(a, self.fmc1.clock.read(a))
            print("------------------------------")