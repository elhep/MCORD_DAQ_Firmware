{
    "core": {
        "type": "local",
        "module": "artiq.coredevice.core",
        "class": "Core",
        "arguments": {
            "host": "192.168.3.203",
            "ref_period": 1e-09
        }
    },
    "core_cache": {
        "type": "local",
        "module": "artiq.coredevice.cache",
        "class": "CoreCache"
    },
    "code_dma": {
        "type": "local",
        "module": "artiq.coredevice.dma",
        "class": "CoreDMA"
    },
    "fmc1_cfd_offset_dac0": {
        "type": "local",
        "module": "elhep_cores.coredevice.dac7578",
        "class": "DAC7578",
        "arguments": {
            "busno": 0,
            "address": 144
        }
    },
    "fmc1_cfd_offset_dac1": {
        "type": "local",
        "module": "elhep_cores.coredevice.dac7578",
        "class": "DAC7578",
        "arguments": {
            "busno": 0,
            "address": 146
        }
    },
    "fmc1_tdc_dis0": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 0
        }
    },
    "fmc1_tdc_dis1": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 1
        }
    },
    "fmc1_tdc_dis2": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 2
        }
    },
    "fmc1_tdc_dis3": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 3
        }
    },
    "fmc1_idx_in": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 4
        }
    },
    "fmc1_adc_resetn": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 5
        }
    },
    "fmc1_adc_sync": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 6
        }
    },
    "fmc1_trig_term": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 7
        }
    },
    "fmc1_trig_dir": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 8
        }
    },
    "fmc1_ref_sel": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 9
        }
    },
    "fmc1_idx_src_sel": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 10
        }
    },
    "fmc1_tdc_spi": {
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {
            "channel": 11
        }
    },
    "fmc1_adc_spi": {
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {
            "channel": 12
        }
    },
    "fmc1_csn0": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 13
        }
    },
    "fmc1_csn1": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 14
        }
    },
    "fmc1_csn2": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 15
        }
    },
    "fmc1_csn3": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 16
        }
    },
    "fmc1_csn4": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 17
        }
    },
    "fmc1_csn5": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 18
        }
    },
    "fmc1_csn6": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 19
        }
    },
    "fmc1_clock_dist": {
        "type": "local",
        "module": "elhep_cores.coredevice.ad9528",
        "class": "AD9528",
        "arguments": {
            "spi_device": "fmc1_tdc_spi",
            "chip_select": "fmc1_csn4"
        }
    },
    "fmc1_adc0_phycsr": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "data0_delay_value",
                    5
                ],
                [
                    "data1_delay_value",
                    5
                ],
                [
                    "data2_delay_value",
                    5
                ],
                [
                    "data3_delay_value",
                    5
                ],
                [
                    "data4_delay_value",
                    5
                ],
                [
                    "data5_delay_value",
                    5
                ],
                [
                    "data6_delay_value",
                    5
                ],
                [
                    "data7_delay_value",
                    5
                ],
                [
                    "data8_delay_value",
                    5
                ],
                [
                    "adclk_delay_value",
                    5
                ],
                [
                    "phy_reset",
                    1,
                    1
                ],
                [
                    "bitslip_done",
                    1,
                    0,
                    "ro"
                ]
            ],
            "channel": 20
        }
    },
    "fmc1_adc0_control": {
        "type": "local",
        "module": "elhep_cores.coredevice.ads5296a",
        "class": "ADS5296A",
        "arguments": {
            "spi_device": "fmc1_adc_spi",
            "phy_csr": "fmc1_adc0_phycsr",
            "chip_select": "fmc1_csn5",
            "spi_freq": 500000
        }
    },
    "fmc1_adc1_phycsr": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "data0_delay_value",
                    5
                ],
                [
                    "data1_delay_value",
                    5
                ],
                [
                    "data2_delay_value",
                    5
                ],
                [
                    "data3_delay_value",
                    5
                ],
                [
                    "data4_delay_value",
                    5
                ],
                [
                    "data5_delay_value",
                    5
                ],
                [
                    "data6_delay_value",
                    5
                ],
                [
                    "data7_delay_value",
                    5
                ],
                [
                    "data8_delay_value",
                    5
                ],
                [
                    "adclk_delay_value",
                    5
                ],
                [
                    "phy_reset",
                    1,
                    1
                ],
                [
                    "bitslip_done",
                    1,
                    0,
                    "ro"
                ]
            ],
            "channel": 21
        }
    },
    "fmc1_adc1_control": {
        "type": "local",
        "module": "elhep_cores.coredevice.ads5296a",
        "class": "ADS5296A",
        "arguments": {
            "spi_device": "fmc1_adc_spi",
            "phy_csr": "fmc1_adc1_phycsr",
            "chip_select": "fmc1_csn6",
            "spi_freq": 500000
        }
    },
    "fmc1_tdc0_phycsr_0": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 22
        }
    },
    "fmc1_tdc0_phycsr_1": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 23
        }
    },
    "fmc1_tdc0_phycsr_2": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 24
        }
    },
    "fmc1_tdc0_phycsr_3": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 25
        }
    },
    "fmc1_tdc0_control": {
        "type": "local",
        "module": "elhep_cores.coredevice.tdc_gpx2",
        "class": "TDCGPX2",
        "arguments": {
            "spi_device": "fmc1_tdc_spi",
            "phy_csr_prefix": "fmc1_tdc0_phycsr_",
            "chip_select": "fmc1_csn0",
            "spi_freq": 1000000
        }
    },
    "fmc1_tdc1_phycsr_0": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 26
        }
    },
    "fmc1_tdc1_phycsr_1": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 27
        }
    },
    "fmc1_tdc1_phycsr_2": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 28
        }
    },
    "fmc1_tdc1_phycsr_3": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 29
        }
    },
    "fmc1_tdc1_control": {
        "type": "local",
        "module": "elhep_cores.coredevice.tdc_gpx2",
        "class": "TDCGPX2",
        "arguments": {
            "spi_device": "fmc1_tdc_spi",
            "phy_csr_prefix": "fmc1_tdc1_phycsr_",
            "chip_select": "fmc1_csn1",
            "spi_freq": 1000000
        }
    },
    "fmc1_tdc2_phycsr_0": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 30
        }
    },
    "fmc1_tdc2_phycsr_1": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 31
        }
    },
    "fmc1_tdc2_phycsr_2": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 32
        }
    },
    "fmc1_tdc2_phycsr_3": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 33
        }
    },
    "fmc1_tdc2_control": {
        "type": "local",
        "module": "elhep_cores.coredevice.tdc_gpx2",
        "class": "TDCGPX2",
        "arguments": {
            "spi_device": "fmc1_tdc_spi",
            "phy_csr_prefix": "fmc1_tdc2_phycsr_",
            "chip_select": "fmc1_csn2",
            "spi_freq": 1000000
        }
    },
    "fmc1_tdc3_phycsr_0": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 34
        }
    },
    "fmc1_tdc3_phycsr_1": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 35
        }
    },
    "fmc1_tdc3_phycsr_2": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 36
        }
    },
    "fmc1_tdc3_phycsr_3": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "frame_length",
                    6,
                    22
                ],
                [
                    "frame_delay_value",
                    5
                ],
                [
                    "data_delay_value",
                    5
                ]
            ],
            "channel": 37
        }
    },
    "fmc1_tdc3_control": {
        "type": "local",
        "module": "elhep_cores.coredevice.tdc_gpx2",
        "class": "TDCGPX2",
        "arguments": {
            "spi_device": "fmc1_tdc_spi",
            "phy_csr_prefix": "fmc1_tdc3_phycsr_",
            "chip_select": "fmc1_csn3",
            "spi_freq": 1000000
        }
    },
    "fmc1_trig": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLInOut",
        "arguments": {
            "channel": 38
        }
    },
    "fmc1_clk0_m2c_ttl_input": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLInOut",
        "arguments": {
            "channel": 39
        }
    },
    "fmc1_clk0_m2c_edge_counter": {
        "type": "local",
        "module": "artiq.coredevice.edge_counter",
        "class": "EdgeCounter",
        "arguments": {
            "channel": 40
        }
    },
    "fmc1_clk1_m2c_ttl_input": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLInOut",
        "arguments": {
            "channel": 41
        }
    },
    "fmc1_clk1_m2c_edge_counter": {
        "type": "local",
        "module": "artiq.coredevice.edge_counter",
        "class": "EdgeCounter",
        "arguments": {
            "channel": 42
        }
    },
    "fmc1_phy_adc0_lclk_input": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLInOut",
        "arguments": {
            "channel": 43
        }
    },
    "fmc1_phy_adc0_lclk_counter": {
        "type": "local",
        "module": "artiq.coredevice.edge_counter",
        "class": "EdgeCounter",
        "arguments": {
            "channel": 44
        }
    },
    "fmc1_phy_adc1_lclk_input": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLInOut",
        "arguments": {
            "channel": 45
        }
    },
    "fmc1_phy_adc1_lclk_counter": {
        "type": "local",
        "module": "artiq.coredevice.edge_counter",
        "class": "EdgeCounter",
        "arguments": {
            "channel": 46
        }
    },
    "fmc1": {
        "type": "local",
        "module": "elhep_cores.coredevice.fmc_adc100M_10b_tdc_16cha",
        "class": "FmcAdc100M10bTdc16cha",
        "arguments": {
            "prefix": "fmc1"
        }
    },
    "fmc1_trigger_reset": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {
            "channel": 47
        }
    },
    "fmc1_adc0_daq0": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 48
        }
    },
    "fmc1_adc0_ch0_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 49
        }
    },
    "fmc1_adc0_daq1": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 50
        }
    },
    "fmc1_adc0_ch1_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 51
        }
    },
    "fmc1_adc0_daq2": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 52
        }
    },
    "fmc1_adc0_ch2_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 53
        }
    },
    "fmc1_adc0_daq3": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 54
        }
    },
    "fmc1_adc0_ch3_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 55
        }
    },
    "fmc1_adc0_daq4": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 56
        }
    },
    "fmc1_adc0_ch4_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 57
        }
    },
    "fmc1_adc0_daq5": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 58
        }
    },
    "fmc1_adc0_ch5_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 59
        }
    },
    "fmc1_adc0_daq6": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 60
        }
    },
    "fmc1_adc0_ch6_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 61
        }
    },
    "fmc1_adc0_daq7": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 62
        }
    },
    "fmc1_adc0_ch7_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 63
        }
    },
    "fmc1_adc0_daq8": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 64
        }
    },
    "fmc1_adc0_ch8_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 65
        }
    },
    "fmc1_adc1_daq0": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 66
        }
    },
    "fmc1_adc1_ch0_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 67
        }
    },
    "fmc1_adc1_daq1": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 68
        }
    },
    "fmc1_adc1_ch1_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 69
        }
    },
    "fmc1_adc1_daq2": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 70
        }
    },
    "fmc1_adc1_ch2_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 71
        }
    },
    "fmc1_adc1_daq3": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 72
        }
    },
    "fmc1_adc1_ch3_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 73
        }
    },
    "fmc1_adc1_daq4": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 74
        }
    },
    "fmc1_adc1_ch4_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 75
        }
    },
    "fmc1_adc1_daq5": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 76
        }
    },
    "fmc1_adc1_ch5_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 77
        }
    },
    "fmc1_adc1_daq6": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 78
        }
    },
    "fmc1_adc1_ch6_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 79
        }
    },
    "fmc1_adc1_daq7": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 80
        }
    },
    "fmc1_adc1_ch7_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 81
        }
    },
    "fmc1_adc1_daq8": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 10,
            "trigger_cnt_width": 4,
            "channel": 82
        }
    },
    "fmc1_adc1_ch8_baseline_tg": {
        "type": "local",
        "module": "elhep_cores.coredevice.rtlink_csr",
        "class": "RtlinkCsr",
        "arguments": {
            "regs": [
                [
                    "offset_level",
                    10
                ]
            ],
            "channel": 83
        }
    },
    "fmc1_tdc0_daq0": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 84
        }
    },
    "fmc1_tdc0_daq1": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 85
        }
    },
    "fmc1_tdc0_daq2": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 86
        }
    },
    "fmc1_tdc0_daq3": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 87
        }
    },
    "fmc1_tdc1_daq0": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 88
        }
    },
    "fmc1_tdc1_daq1": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 89
        }
    },
    "fmc1_tdc1_daq2": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 90
        }
    },
    "fmc1_tdc1_daq3": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 91
        }
    },
    "fmc1_tdc2_daq0": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 92
        }
    },
    "fmc1_tdc2_daq1": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 93
        }
    },
    "fmc1_tdc2_daq2": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 94
        }
    },
    "fmc1_tdc2_daq3": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 95
        }
    },
    "fmc1_tdc3_daq0": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 96
        }
    },
    "fmc1_tdc3_daq1": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 97
        }
    },
    "fmc1_tdc3_daq2": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 98
        }
    },
    "fmc1_tdc3_daq3": {
        "type": "local",
        "module": "elhep_cores.coredevice.circular_daq",
        "class": "CircularDaq",
        "arguments": {
            "data_width": 22,
            "trigger_cnt_width": 4,
            "channel": 99
        }
    },
    "sw_trigger_0": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 100
        }
    },
    "sw_trigger_1": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 101
        }
    },
    "sw_trigger_2": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 102
        }
    },
    "sw_trigger_3": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 103
        }
    },
    "sw_trigger_4": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 104
        }
    },
    "sw_trigger_5": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 105
        }
    },
    "sw_trigger_6": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 106
        }
    },
    "sw_trigger_7": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 107
        }
    },
    "sw_trigger_8": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 108
        }
    },
    "sw_trigger_9": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 109
        }
    },
    "sw_trigger_10": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 110
        }
    },
    "sw_trigger_11": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 111
        }
    },
    "sw_trigger_12": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 112
        }
    },
    "sw_trigger_13": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 113
        }
    },
    "sw_trigger_14": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 114
        }
    },
    "sw_trigger_15": {
        "type": "local",
        "module": "elhep_cores.coredevice.trigger_generator",
        "class": "RtioTriggerGenerator",
        "arguments": {
            "channel": 115
        }
    },
    "trigger_controller": {
        "type": "local",
        "module": "coredevice.trigger_controller",
        "class": "TriggerController",
        "arguments": {
            "layout": "trigger_controller_layout.json",
            "channel": 116
        }
    }
}