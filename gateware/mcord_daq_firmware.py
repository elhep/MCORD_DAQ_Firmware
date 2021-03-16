import argparse
import os

from migen import *
from artiq.build_soc import build_artiq_soc
from artiq.gateware import rtio

from misoc.integration.builder import builder_args, builder_argdict
from misoc.cores import uart
from misoc.targets.afck1v1 import soc_afck1v1_argdict, soc_afck1v1_args

from elhep_cores.cores.fmc_adc100M_10B_tdc_16cha import FmcAdc100M10b16chaTdc
from elhep_cores.cores.xilinx_ila import ILAProbeAsync, ILAProbe, add_xilinx_ila, xilinx_ila_args
from elhep_cores.cores.trigger_controller.trigger_generators import RtioBaselineTriggerGenerator
from elhep_cores.cores.trigger_controller.trigger_controller import RtioTriggerController

from elhep_cores.targets.afck1v1 import StandaloneBase, iostd_single, iostd_diff
from elhep_cores.cores.circular_daq.circular_daq import CircularDAQ


class AfckTdc(StandaloneBase):

    def __init__(self, with_fmc1=False, with_fmc2=False, with_ila=False, ila_depth=1024, **kwargs):
        self.with_fmc1 = with_fmc1
        self.with_fmc2 = with_fmc2
        self.with_ila = with_ila

        self.adc_daq_samples = 1024
        self.tdc_daq_samples = 1024
        self.trigger_cnt_width = 4

        self.trigger_generators = []
        self.trigger_channels = []
        
        super().__init__(**kwargs)
        
    def add_design(self):
        assert self.with_fmc1 or self.with_fmc2, "At least one FMC must be enabled"

        if self.with_fmc1:
            self.add_fmc(1)
        if self.with_fmc2:
            self.add_fmc(2)

        self.submodules.trigger_controller = RtioTriggerController(
            trigger_generators=self.trigger_generators,
            trigger_channels=self.trigger_channels,
            rtlink_triggers_no=4,
            signal_delay=23
        )
        self.add_rtio_channels(
                channel=rtio.Channel.from_phy(self.trigger_controller), 
                device_id=f"trigger_controller",
                module="elhep_cores.coredevice.trigger_controller",
                class_name="TriggerController")

        if self.with_ila:
            print("Building with ILA")
            self.submodules += [
                ILAProbe(self.fmc1_adc0_daq0_baseline_tg.trigger_re, "fmc1_adc0_daq0_trigger_re"),
                ILAProbe(self.fmc1_adc0_daq0_baseline_tg.trigger_fe, "fmc1_adc0_daq0_trigger_fe"),
                ILAProbe(self.fmc1_adc0_daq0_baseline_tg.trigger_level_offset, "fmc1_adc0_daq0_trigger_level_offset"),
                ILAProbe(self.fmc1_adc0_daq0_baseline_tg.trigger_level, "fmc1_adc0_daq0_trigger_level"),
                ILAProbe(self.fmc1_adc0_phy.data_o[0], "fmc1_adc0_phy_data0"),
                ILAProbe(self.fmc1_adc0_phy.data_o[1], "fmc1_adc0_phy_data0"),
                ILAProbe(self.fmc1_adc0_phy.bitslip_done, "fmc1_adc0_phy_bitslip_done"),                
                ILAProbe(self.fmc1_adc0_daq0.trigger_dclk, "fmc1_adc0_daq0_trigger"),
                ILAProbe(self.fmc1_adc0_daq0.posttrigger_dclk, "fmc1_adc0_daq0_posttrigger"),
                ILAProbe(self.fmc1_adc0_daq0.pretrigger_dclk, "fmc1_adc0_daq0_pretrigger"),
            ]
            debug_clock = self.crg.cd_sys.clk
            add_xilinx_ila(target=self, debug_clock=debug_clock, depth=2048)


        # sclk = self.platform.request("vcxo_dac_sclk") 
        # mosi = self.platform.request("vcxo_dac_din") 
        # syncn = [
        #     self.platform.request("vcxo_dac1_sync_n"),
        #     self.platform.request("vcxo_dac2_sync_n")
        # ]
        # ncs = Signal()

        # phy = DacSpi(sclk, mosi, ncs)
        # self.submodules += phy
        # self.comb += [s.eq(ncs) for s in syncn]

    def add_fmc(self, fmc_idx):        
        FmcAdc100M10b16chaTdc.add_std(self, fmc_idx, iostd_single, iostd_diff, with_trig=True)

        for adc_idx in range(2):
            self.add_adc(fmc_idx, adc_idx)
        
        for tdc_idx in range(4):
            self.add_tdc(fmc_idx, tdc_idx)
        
    def add_adc(self, fmc_idx, adc_idx):
        prefix = f"fmc{fmc_idx}_adc{adc_idx}"
        cd_renamer = ClockDomainsRenamer({"dclk": f"{prefix}_dclk"})
        phy = getattr(self, f"{prefix}_phy")

        for channel in range(9):
            trigger = Signal()
            self.trigger_channels.append(
                {"signal": trigger, "label": f"{prefix}_daq{channel}"}
            )

            daq = cd_renamer(CircularDAQ(
                data_i=phy.data_o[channel],
                stb_i=1,
                trigger_rio_phy=trigger,
                circular_buffer_length=self.adc_daq_samples
            ))
            setattr(self.submodules, f"{prefix}_daq{channel}", daq)
            self.add_rtio_channels(
                channel=rtio.Channel.from_phy(daq, ififo_depth=self.adc_daq_samples), 
                device_id=f"{prefix}_daq{channel}",
                module="elhep_cores.coredevice.circular_daq",
                class_name="CircularDaq")
            
            baseline_tg = cd_renamer(RtioBaselineTriggerGenerator(
                data=phy.data_o[channel],
                name=f"{prefix}_daq{channel}_baseline_tg"
            ))
            setattr(self.submodules, f"{prefix}_daq{channel}_baseline_tg", baseline_tg)
            self.trigger_generators.append(baseline_tg)
            self.add_rtio_channels(
                channel=rtio.Channel.from_phy(baseline_tg.csr),
                device_id=f"fmc{fmc_idx}_tdc{adc_idx}_ch{channel}_baseline_tg",
                module="elhep_cores.coredevice.rtlink_csr",
                class_name="RtlinkCsr",
                arguments={
                    "regs": baseline_tg.csr.regs
            })

    def add_tdc(self, fmc_idx, tdc_idx):
        prefix = f"fmc{fmc_idx}_tdc{tdc_idx}"
        cd_renamer = ClockDomainsRenamer({"dclk": f"{prefix}_dclk"})
        phy = getattr(self, f"{prefix}_phy")

        for channel in range(4):
            trigger = Signal()
            self.trigger_channels.append(
                {"signal": trigger, "label": f"{prefix}_daq{channel}"}
            )

            daq = cd_renamer(CircularDAQ(
                data_i=phy.data_o[channel][:32-self.trigger_cnt_width],
                stb_i=phy.data_stb_o[channel],
                trigger_rio_phy=trigger,
                circular_buffer_length=self.tdc_daq_samples
            ))
            setattr(self.submodules, f"{prefix}_daq{channel}", daq)
            self.add_rtio_channels(
                channel=rtio.Channel.from_phy(daq, ififo_depth=self.tdc_daq_samples), 
                device_id=f"{prefix}_daq{channel}",
                module="elhep_cores.coredevice.circular_daq",
                class_name="CircularDaq")
   

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
    parser.set_defaults(output_dir="mcord_daq_fw")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    soc = AfckTdc(**mcord_argdict(args), output_dir=args.output_dir)
    build_artiq_soc(soc, builder_argdict(args))


if __name__ == "__main__":
    main()


















