from migen import *
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer


class MCORDConstants:

    trigger_id_width = 4
    


def cdc(target, signal_i, idomain, odomain):
    if len(signal_i) == 1:
        cdc = PulseSynchronizer(idomain, odomain)
    else:
        cdc = BusSynchronizer(len(signal_i), idomain, odomain)
    target.submodules += cdc
    target.comb += cdc.i.eq(signal_i)
    return cdc.o

