from artiq.gateware.targets.afck1v1 import StandaloneBase, iostd_single, iostd_diff
from design.cores.fmc_adc100M_10B_tdc_16cha import FmcAdc100M10b16chaTdc

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.genlib.cdc import MultiReg
from migen.build.generic_platform import *
from migen.genlib.io import DifferentialOutput

from misoc.interconnect.csr import *
from misoc.cores import gpio
from misoc.cores.a7_gtp import *
from misoc.targets.afck1v1 import MiniSoC, BaseSoC, soc_afck1v1_argdict, soc_afck1v1_args
from misoc.integration.soc_sdram import soc_sdram_argdict
from misoc.integration.builder import builder_args, builder_argdict

from artiq.gateware.amp import AMPSoC
from artiq.gateware import rtio
from artiq.build_soc import build_artiq_soc, add_identifier
from artiq.gateware.rtio.phy.ttl_simple import Output


class AfckTdc(StandaloneBase):

    def add_design(self):
        FmcAdc100M10b16chaTdc.add_std(self, 1, iostd_single, iostd_diff)
        FmcAdc100M10b16chaTdc.add_std(self, 2, iostd_single, iostd_diff)


def main():
    parser = argparse.ArgumentParser(
        description="ARTIQ device binary builder for AFCK 1v1 systems")
    builder_args(parser)
    soc_afck1v1_args(parser)
    parser.set_defaults(output_dir="artiq_afck1v1")
    args = parser.parse_args()

    soc = AfckTdc(**soc_afck1v1_argdict(args))
    build_artiq_soc(soc, builder_argdict(args))


if __name__ == "__main__":
    main()

