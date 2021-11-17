from migen import *
from elhep_cores.cores.pulse_extender import PulseExtender


class CoincidenceDetector(Module):

    def __init__(self, width, detection_window_max_length=255):
        self.trigger_i = Signal(width)
        self.trigger_o = Signal()
        self.enabled_i = Signal()
        self.mask_i = Signal.like(self.trigger_i)
        self.detection_window_i = Signal(max=detection_window_max_length)

        # # #

        assert width <= 32, "Number of input signals must be <= 32"

        pulses = []

        for idx, signal in enumerate(self.trigger_i):
            pe = PulseExtender(detection_window_max_length)
            setattr(self.submodules, f"pe_{idx}", pe)
            self.comb += [
                pe.i.eq(signal),
                pe.length.eq(self.detection_window_i)
            ]
            pulses.append(pe.o)

        product_elements = [(pulses[i] | ~mask_i.mask[i]) for i in range(len(pulses))]
        product_elements.append(self.enabled_i)
        product = reduce(and_, product_elements)

        trigger_int = Signal()
        trigger_int_d = Signal()
        self.sync += [
            self.trigger_o.eq(trigger_int & ~trigger_int_d),
            trigger_int_d.eq(trigger_int),
            trigger_int.eq(product)
        ]


# TODO: Verification