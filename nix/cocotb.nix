{pkgs}:

pkgs.python3Packages.buildPythonPackage rec {
    name = "cocotb";
    src = pkgs.fetchFromGitHub {
      owner = "cocotb";
      repo = "cocotb";
      rev = "17ce4e51da43b6d2d1b5834d629374ed5535a8d8";
      sha256 = "0wp5xc3fyk1a4bmf18m778zmbswjrnz34qik2h7ds14j3fpl26m1";
    };
    doCheck = false;
    propagatedBuildInputs = [ pkgs.verilog ];
  }
