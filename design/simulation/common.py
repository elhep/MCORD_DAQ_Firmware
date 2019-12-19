import os


def update_tb(verilog_path):
    with open(verilog_path) as f:
        design = f.read()

    design = design.replace("/* Machine-generated using Migen */", """/* Machine-generated using Migen */

`timescale 1ns/1ps
""")
    design = design.replace("endmodule", """`ifdef COCOTB_SIM
initial begin
  $dumpfile ("top.vcd");
  $dumpvars (0, top);
  #1;
end
`endif

endmodule
""")

    with open(verilog_path, 'w') as f:
        f.write(design)


def generate_cocotb_tb(platform, module, build_dir="./build"):
    platform.build(module, build_dir=build_dir, run=False)
    update_tb(os.path.join(build_dir, "top.v"))



