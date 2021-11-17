from migen import *


class BaselineGenerator(Module):

    def __init__(self, data_width):
        self.data_i = Signal(data_width)
        self.data_o = Signal(data_width)

        # # #

        # FIXME: Move baseline implementation here
        self.comb += [
            self.data_o.eq(self.data_i)
        ]
