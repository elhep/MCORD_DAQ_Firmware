from migen import *


class Integral(Module):

    def __init__(self, data_width, sum_width):
        self.data_i = Signal(data_width)
        self.data_valid_i = Signal()
        self.data_o = Signal(sum_width)
        self.data_valid_o = Signal()

        # # #

        # TODO: Implementation
        