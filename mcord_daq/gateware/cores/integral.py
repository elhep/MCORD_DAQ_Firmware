from migen import *
from misoc.interconnect.stream import Endpoint


class Integral(Module):

    def __init__(self, data_width, max_samples=100):
        self.sink = Endpoint([("data", data_width)])
        sum_width = len(Signal(max=(2**data_width-1)*max_samples))
        self.source = Endpoint([("data", sum_width)])

        # # #

        # TODO: Implementation
        