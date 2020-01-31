from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint
from coredevice.fmc_adc100M_10b_tdc_16cha import FmcAdc100M10bTdc16cha


class TestComm(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("fmc1")

        self.fmc1 = self.get_device("fmc1")  # type: FmcAdc100M10bTdc16cha

    @kernel
    def test_adc_comm(self):
        self.core.break_realtime()
        self.fmc1.adc[0].write_rt(0xA, 0xF00F)
        self.fmc1.adc[0].enable_read_rt()
        r = self.fmc1.adc[0].read_rt(0xA)
        delay(100 * us)
        self.fmc1.adc[0].disable_read_rt()
        return r

    @kernel
    def test_daq(self):
        self.core.break_realtime()
        # self.fmc1.adc[0].daq[0].clear_fifo()
        self.fmc1.adc[0].daq[8].configure(20, 20)
        delay(100 * us)
        self.fmc1.adc[0].daq[8].trigger()
        delay(100 * us)
        self.fmc1.adc[0].daq[8].get_samples()

    @kernel
    def clear_adc_rtio(self):
        self.fmc1.adc[0].daq[0].clear_fifo()

    @kernel
    def debug_daq(self):
        self.core.break_realtime()
        self.fmc1.adc[0].daq[8].configure(20, 20)

    def run(self):
        self.fmc1.initialize()
        #
        # self.fmc1.adc[0].write(0x46, 0x8108)
        # self.fmc1.adc[0].write(0x45, 0x0)
        # self.fmc1.adc[0].write(0x25, 0x40)

        # self.debug_daq()
        # self.clear_adc_rtio()

        # for i in range(32):
        #     while True:
        #         self.fmc1.adc[0].phy.adclk_delay_value.write(i)
        #         self.test_daq()
        #         print("Samples:")
        #         for s in self.fmc1.adc[0].daq[8].samples:
        #             print(bin(s))
        #         a = input("{}, next value (n), repeat (r)".format(i))
        #         if a == 'n':
        #             break
        #         elif a == 'r':
        #             continue
        #         else:
        #             continue

        # self.fmc1.adc[0].daq[8].get_samples()






