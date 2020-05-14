core_addr = "192.168.95.202"

device_db = {
    "core": {
        "type": "local",
        "module": "artiq.coredevice.core",
        "class": "Core",
        "arguments": {"host": core_addr, "ref_period": 1e-9}
    },
    "core_log": {
        "type": "controller",
        "host": "::1",
        "port": 1068,
        "command": "aqctl_corelog -p {port} --bind {bind} " + core_addr
    },
    "core_cache": {
        "type": "local",
        "module": "artiq.coredevice.cache",
        "class": "CoreCache"
    },
    "core_dma": {
        "type": "local",
        "module": "artiq.coredevice.dma",
        "class": "CoreDMA"
    },

    "fmc1": {
        "type": "local",
        "module": "coredevice.fmc_adc100M_10b_tdc_16cha",
        "class": "FmcAdc100M10bTdc16cha",
        "arguments": {"channel": 0x0, "with_trig": True}
    },
}
