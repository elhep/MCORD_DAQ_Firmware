import argparse
import os

from migen import *
from migen.genlib.cdc import BusSynchronizer

from artiq.build_soc import build_artiq_soc
from artiq.gateware import rtio
from artiq.gateware.rtio.phy.ttl_simple import Output

from misoc.integration.builder import builder_args, builder_argdict
from misoc.cores import uart

from elhep_cores.targets.misoc.afck1v1 import (
    soc_afck1v1_argdict, soc_afck1v1_args
)
from elhep_cores.cores.fmc_adc100M_10B_tdc_16cha import FmcAdc100M10b16chaTdc
from elhep_cores.cores.xilinx_ila import (
    ILAProbeAsync, ILAProbe, add_xilinx_ila, xilinx_ila_args
)
from elhep_cores.cores.trigger_generators import (
    RtioBaselineTriggerGenerator, RtioTriggerGenerator, ExternalTriggerInput
)
from elhep_cores.targets.artiq.afck1v1 import (
    StandaloneBase, iostd_single, iostd_diff
)
from elhep_cores.cores.circular_daq.circular_daq import CircularDAQ
from elhep_cores.cores.dac_spi import DacSpi

from mcord_daq.gateware.trigger_controller.trigger_controller import TriggerController


class AfckTdc(StandaloneBase):

    def __init__(self, with_fmc1=True, with_fmc2=False, with_ila=False, 
            ila_depth=1024, **kwargs):
        self.with_fmc1 = with_fmc1
        self.with_fmc2 = with_fmc2
        self.with_ila = with_ila

        self.adc_daq_samples = 1024
        self.tdc_daq_samples = 1024
        self.trigger_id_width = 8

        self.trigger_generators = []
        self.trigger_channels = []
        
        super().__init__(**kwargs)
        
    def add_design(self):
        self.add_vcxo_dac()
        
        channel_offset = 0
        detector_offset = 0
        if self.with_fmc1:
            self.add_fmc(1)
            for i in range(8):
                self.add_detector(
                    detector_idx=detector_offset+i, 
                    channel_offset=channel_offset+2*i, 
                    fmc="fmc1", 
                    coincidence_module=f"trigger_controller_l0_{detector_offset+i}", 
                    trigger_controller="trigger_controller"
                )
            detector_offset += 8
            channel_offset += 16
            
        if self.with_fmc2:
            self.add_fmc(2)
            for i in range(8):
                self.add_detector(
                    detector_idx=detector_offset+i, 
                    channel_offset=channel_offset+2*i, 
                    fmc="fmc1", 
                    coincidence_module=f"trigger_controller_l0_{detector_offset+i}", 
                    trigger_controller="trigger_controller"
                )

        self.add_triggering(sw_triggers=8)                

        if self.with_ila:
            self.add_ila()

    def add_detector(self, detector_idx, channel_offset, fmc, coincidence_module,
            trigger_controller="trigger_controller"):
        self.register_coredevice(
            device_id=f"detector_{detector_idx}",
            module="mcord_daq.coredevice.detector",
            class_name="Detector",
            arguments={
                "fmc": fmc,
                "channel_a": channel_offset,
                "channel_b": channel_offset+1,
                "coincidence_module": coincidence_module
            }
        )

    def add_vcxo_dac(self):
        sclk = self.platform.request("vcxo_dac_sclk") 
        mosi = self.platform.request("vcxo_dac_din") 
        syncn = [
            self.platform.request("vcxo_dac1_sync_n"),
            self.platform.request("vcxo_dac2_sync_n")
        ]
        ncs = Signal()
        phy = DacSpi(sclk, mosi, ncs)
        self.submodules += phy
        self.comb += [s.eq(ncs) for s in syncn]

    def add_triggering(self, sw_triggers=8):
        # External trigger
        trigger_pads = self.platform.request("fmc1_trig")
        ext_trig = ClockDomainsRenamer("rio_phy")(
            ExternalTriggerInput(trigger_pads.p, trigger_pads.n)
        )
        self.submodules.ext_trig = ext_trig
        self.trigger_generators.append(ext_trig)

        for idx in range(sw_triggers):
            sw_trig = RtioTriggerGenerator(f"sw_trigger_{idx}", identifier=f"sw_trigger_{idx}")
            setattr(self.submodules, f"sw_trigger_{idx}", sw_trig)
            self.trigger_generators.append(sw_trig)

        trigger_controller = TriggerController(self.trigger_generators, 
            l0_num=8, l1_num=8, l1_extra=[ext_trig], outputs=self.trigger_channels, 
            with_ila=self.with_ila)
        self.submodules.trigger_controller = trigger_controller

    def add_fmc(self, fmc_idx):        
        FmcAdc100M10b16chaTdc.add_std(self, fmc_idx, iostd_single, iostd_diff, with_trig=False)

        for adc_idx in range(2):
            self.add_adc(fmc_idx, adc_idx)
        
        for tdc_idx in range(4):
            self.add_tdc(fmc_idx, tdc_idx)
        
    def add_adc(self, fmc_idx, adc_idx):
        prefix = f"fmc{fmc_idx}_adc{adc_idx}"
        phy = getattr(self, f"{prefix}_phy")

        for channel in range(9):
            # Create and keep trigger signals
            trigger_rio_phy = Signal()
            trigger_id = Signal(self.trigger_id_width)
            self.trigger_channels.append({
                "trigger": trigger_rio_phy, 
                "trigger_id": trigger_id, 
                "label": f"{prefix}_daq{channel}"
            })

            # CDC for triggering (rio_phy -> dclk)
            trigger_dclk = Signal()
            trigger_id_dclk = Signal.like(trigger_id)
            dclk_name = f"{prefix}_dclk"
            cdc = BusSynchronizer(self.trigger_id_width+1, "rio_phy", dclk_name)
            self.submodules += cdc
            self.comb += [
                cdc.i.eq(Cat(trigger_rio_phy, trigger_id)),
                Cat(trigger_dclk, trigger_id_dclk).eq(cdc.o)
            ]

            # DAQ instance
            daq = ClockDomainsRenamer({"dclk": dclk_name})(CircularDAQ(
                data_i=phy.data_o[channel],
                stb_i=1,
                trigger_dclk=trigger_dclk,
                trigger_id_dclk=trigger_id_dclk,
                circular_buffer_length=self.adc_daq_samples
            ))
            setattr(self.submodules, f"{prefix}_daq{channel}", daq)
            self.add_rtio_channels(
                channel=rtio.Channel.from_phy(daq, ififo_depth=8*self.adc_daq_samples), 
                device_id=f"{prefix}_daq{channel}",
                module="mcord_daq.coredevice.wrappers",
                class_name="MCORDCircularDaq",
                arguments={
                    "data_mapping": [
                        ("sample", 10),
                        ("l1_idx", 4),
                        ("l1_cnt", 4),                                             
                    ],
                    "buffer_len": 8192
                })
            
            # Trigger generator instance
            baseline_tg = ClockDomainsRenamer({"sys": f"{prefix}_dclk"})(RtioBaselineTriggerGenerator(
                data=phy.data_o[channel],
                name=f"{prefix}_ch{channel}_baseline_tg"
            ))
            setattr(self.submodules, f"{prefix}_ch{channel}_baseline_tg", baseline_tg)
            self.trigger_generators.append(baseline_tg)
            self.add_rtio_channels(
                channel=rtio.Channel.from_phy(baseline_tg.csr),
                device_id=f"{prefix}_ch{channel}_baseline_tg",
                module="elhep_cores.coredevice.rtlink_csr",
                class_name="RtlinkCsr",
                arguments={
                    "regs": baseline_tg.csr.regs
            })

    def add_tdc(self, fmc_idx, tdc_idx):
        prefix = f"fmc{fmc_idx}_tdc{tdc_idx}"
        phy = getattr(self, f"{prefix}_phy")

        for channel in range(4):
            # Create and keep trigger signals
            trigger_rio_phy = Signal()
            trigger_id = Signal(self.trigger_id_width)
            self.trigger_channels.append({
                "trigger": trigger_rio_phy, 
                "trigger_id": trigger_id,
                "label": f"{prefix}_daq{channel}"
            })

            # CDC for triggering (rio_phy -> dclk)
            trigger_dclk = Signal()
            trigger_id_dclk = Signal.like(trigger_id)
            dclk_name = f"{prefix}_dclk"
            cdc = BusSynchronizer(self.trigger_id_width+1, "rio_phy", dclk_name)
            self.submodules += cdc
            self.comb += [
                cdc.i.eq(Cat(trigger_rio_phy, trigger_id)),
                Cat(trigger_dclk, trigger_id_dclk).eq(cdc.o)
            ]

            # DAQ instance
            daq = ClockDomainsRenamer({"dclk": f"{prefix}_dclk"})(CircularDAQ(
                data_i=phy.data_o[channel][:24],
                stb_i=phy.data_stb_o[channel],
                trigger_dclk=trigger_dclk,
                trigger_id_dclk=trigger_id_dclk,
                circular_buffer_length=self.tdc_daq_samples
            ))
            setattr(self.submodules, f"{prefix}_daq{channel}", daq)
            self.add_rtio_channels(
                channel=rtio.Channel.from_phy(daq, ififo_depth=self.tdc_daq_samples), 
                device_id=f"{prefix}_daq{channel}",
                module="mcord_daq.coredevice.wrappers",
                class_name="MCORDCircularDaq",
                arguments={
                    "data_mapping": [
                        ("sample", 24),
                        ("l1_idx", 4),
                        ("l1_cnt", 4),                                             
                    ],
                    "buffer_len": 8192
                })

    def add_ila(self):

        def adc_daq_debug(fmc, adc, daq):
            prefix = f"fmc{fmc}_adc{adc}_daq{daq}"
            daq = getattr(self, f"{prefix}")
            return [
                ILAProbe(daq.trigger_dclk, f"{prefix}_trigger"),
                ILAProbe(daq.trigger_id_dclk, f"{prefix}_trigger_id"),
                ILAProbe(daq.data_i, f"{prefix}_data_i"),
                ILAProbe(daq.rtlink.i.stb, f"{prefix}_rtlink_stb_i"),                 
                ILAProbe(daq.rtlink.i.data, f"{prefix}_rtlink_data_i")
            ]

        def adc_phy_debug(fmc, adc, channels):
            phy = getattr(self, f"fmc{fmc}_adc{adc}_phy")
            prefix = f"fmc{fmc}_adc{adc}_phy"
            return [
                *([ILAProbe(phy.data_o[c], f"{prefix}_data{c}") for c in channels]),
                ILAProbe(phy.bitslip_done, f"{prefix}_bitslip_done")
            ]

        def tdc_phy_debug(fmc, tdc, channels):
            phy = getattr(self, f"fmc{fmc}_tdc{tdc}_phy")
            prefix = f"fmc{fmc}_tdc{tdc}_phy"
            return [
                *([ILAProbe(phy.phy_channels[c].data_o, f"{prefix}_data{c}") for c in channels]),
                *([ILAProbe(phy.phy_channels[c].stb_o, f"{prefix}_stb{c}") for c in channels]),
                *([ILAProbe(phy.phy_channels[c].frame_start, f"{prefix}_frame_start{c}") for c in channels]),
                *([ILAProbe(phy.phy_channels[c].csr.frame_length, f"{prefix}_frame_length{c}") for c in channels])
            ]

        def tdc_daq_debug(fmc, tdc, daq):
            prefix = f"fmc{fmc}_tdc{tdc}_daq{daq}"
            daq = getattr(self, f"{prefix}")
            return [
                ILAProbe(daq.trigger_dclk, f"{prefix}_trigger"),
                ILAProbe(daq.posttrigger_dclk, f"{prefix}_posttrigger"),
                ILAProbe(daq.pretrigger_dclk, f"{prefix}_pretrigger")                    
            ]

        print("Building with ILA")
        self.submodules += [
            # *(adc_phy_debug(1, 1, [0, 1, 2, 3, 4, 5, 6, 7])),
            *(adc_phy_debug(1, 0, [2, 3])),
            # *(tdc_phy_debug(1, 0, [0, 1, 2, 3])),
            # *(tdc_phy_debug(1, 1, [0, 1, 2, 3])),
            # *(tdc_phy_debug(1, 2, [0, 1, 2, 3])),
            # *(tdc_phy_debug(1, 3, [0, 1, 2, 3])),
            # *(adc_daq_debug(1, 1, 4)),
            # *(adc_daq_debug(1, 0, 0)),
            # *(adc_daq_debug(1, 0, 1)),
            # *(adc_daq_debug(1, 0, 2)),
            # *(adc_daq_debug(1, 0, 3)),
            # *(tdc_daq_debug(1, 3, 3)),
            # *(tdc_daq_debug(1, 3, 2)),
        ]
        debug_clock = self.crg.cd_sys.clk
        add_xilinx_ila(target=self, debug_clock=debug_clock, output_dir=self.output_dir, depth=1024)
   

def mcord_argdict(args):
    r = soc_afck1v1_argdict(args)
    r["with_fmc1"] = args.with_fmc1
    r["with_fmc2"] = args.with_fmc2
    r["with_ila"] = args.with_ila
    return r


def main():
    parser = argparse.ArgumentParser(
        description="MCORD DAQ firmware builder for platform AFCK v1.1")
    builder_args(parser)
    soc_afck1v1_args(parser)
    xilinx_ila_args(parser)
    parser.add_argument("--with-fmc1", action="store_true", help="Add FMC TDC to FMC1")
    parser.add_argument("--with-fmc2", action="store_true", help="Add FMC TDC to FMC2")
    parser.set_defaults(output_dir="build")
    args = parser.parse_args()

    if args.integrated_rom_size:
        args.integrated_rom_bin = os.path.join(args.output_dir, "software", "bootloader", "bootloader.bin")

    os.makedirs(args.output_dir, exist_ok=True)

    soc = AfckTdc(**mcord_argdict(args), output_dir=args.output_dir)
    build_artiq_soc(soc, builder_argdict(args))


if __name__ == "__main__":
    main()


















