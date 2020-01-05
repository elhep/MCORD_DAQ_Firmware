{ pkgs ? import <nixpkgs> {}, repo }:

let
  artiqpkgs = import ../modules/nix-scripts/artiq-fast/default.nix { inherit pkgs; };
  cocotb = import ./cocotb.nix { inherit pkgs; };
in
  pkgs.mkShell {
    buildInputs = [
#       vivado
      pkgs.gnumake
      (pkgs.python3.withPackages(ps: (with ps; [ jinja2 numpy paramiko ]) ++ (with artiqpkgs; [ migen microscope misoc jesd204b migen-axi artiq ])))
      pkgs.cargo
      artiqpkgs.rustc
      artiqpkgs.binutils-or1k
      artiqpkgs.binutils-arm
      artiqpkgs.llvm-or1k
      artiqpkgs.openocd
      cocotb
      pkgs.gtkwave
    ] ++ (with pkgs; [
      ncurses5
      zlib
      libuuid
      xorg.libSM
      xorg.libICE
      xorg.libXrender
      xorg.libX11
      xorg.libXext
      xorg.libXtst
      xorg.libXi
    ]);
    TARGET_AR="or1k-linux-ar";
    shellHook = "source nix/fixpythonpath";
  }
