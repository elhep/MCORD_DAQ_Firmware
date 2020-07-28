from artiq.experiment import *
from artiq.language.units import ns, us
from pprint import pprint
from artiq.coredevice.i2c import *


class ConfigureAfckClocking(EnvExperiment):

    def build(self):
        self.setattr_device("core")     
        self.setattr_device("i2c_mux")     

    @kernel
    def run(self):
        # while True:
            #try:
        self.i2c_mux.set(0)
            #except:
            #    pass
        # print(self.i2c_mux.readback())
        for i in range(128):
            print(i << 1, i2c_poll(0, i << 1))
