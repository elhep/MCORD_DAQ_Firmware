# FMC ADC 100M 10b TDC 16cha @ AFCK using ARTIQ

This repository contains FMC ADC 100M 10b TDC 16cha support for ARTIQ system. 
It consists of several gateware modules and coredevice drivers. 

## Repository structure

### `gateware`

This directory relates to ARTIQ gateware directory and contains hardware description
designed using Migen.

For more information refere to the `gateware.md`.

### `coredevice`

Coredevices are ARTIQ software drivers. This repository provides basic drivers
for all gateware modules provided and driver integration for FMC module.

For more information refere to the `coredevices.md`.

### `modules`

Required submodules are defined in `modules` directory. They point to specific 
commits that are known to work with this design.

There are several submodules:

- `artiq` - ARTIQ control system, special version with AFCK support
- `misoc` - MiSoC repository with AFCK support
- `migen` - original M-Labs Migen repository
- `cocotb` - CocoTB framework for writing HDL testbenches in Python
- `liteiclink` - dependency of MiSoC AFCK port (GTX support)
- `nix-scripts` - original M-Labs repository providing Nix expressions for 
  ARTIQ environment generation
  
### `nix`

Nix expressions for design related environment customisations.

## Using this repository

### Nix installation 

As ARTIQ uses Nix for dependency and environment management you need to install 
Nix package manager first. As non-root user type:

```bash
curl https://nixos.org/nix/install | sh
```

This script will download a distribution-independent binary tarball containing 
Nix and its dependencies, and unpack it in `/nix`.

### Cloning this repository

Please note that you must clone repository along with all submodules (`--recursive` option):

```bash
git clone --recursive https://github.com/elhep/FMC_ADC100M_10B_TDC_16cha_gw.git
```

### Creating development environment

There is a simple script `start_dev_shell` that makes starting development environment easier.

**WARNING:** Script assumes it is run frome the repository root!

```bash
./start_dev_shell
```

### Building gateware

To build gateware for AFCK with two FMC cards mounted use the following command:

```bash
python ./gateare/afck_tdc.py
```

This will build gateare and firmware to be flashed to AFCK SPI flash memory.

