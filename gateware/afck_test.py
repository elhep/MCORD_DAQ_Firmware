import argparse

from artiq.build_soc import build_artiq_soc
from artiq.gateware.targets.afck1v1 import StandaloneBase, iostd_single, iostd_diff
from gateware.cores.fmc_adc100M_10B_tdc_16cha import FmcAdc100M10b16chaTdc
from misoc.integration.builder import builder_args, builder_argdict
from misoc.targets.afck1v1 import soc_afck1v1_argdict, soc_afck1v1_args
from artiq.gateware.rtio.phy.ttl_simple import Output
from artiq.gateware.rtio import Channel


class AfckTest(StandaloneBase):

    def add_design(self):
        led_pads = [self.platform.request("led", i) for i in range(3)]
        led_phy = [Output(p) for p in led_pads]
        for i, phy in enumerate(led_phy):
            self.submodules += phy
            self.rtio_channels.append(Channel.from_phy(phy))
            self.rtio_channel_labels.append("LED_{}".format(i))


def main():
    parser = argparse.ArgumentParser(
        description="ARTIQ device binary builder for AFCK 1v1 systems")
    builder_args(parser)
    soc_afck1v1_args(parser)
    parser.set_defaults(output_dir="artiq_afck_test")
    args = parser.parse_args()

    soc = AfckTest(**soc_afck1v1_argdict(args))
    build_artiq_soc(soc, builder_argdict(args))


if __name__ == "__main__":
    main()

