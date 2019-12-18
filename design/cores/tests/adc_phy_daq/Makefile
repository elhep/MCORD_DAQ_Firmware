VERILOG_SOURCES = /home/ms/Software/Xilinx/Vivado/2017.4/data/verilog/src/glbl.v $(PWD)/../build/top.v
TOPLEVEL=top
MODULE=tdc_iface_test

COMPILE_ARGS=-y/home/ms/Software/Xilinx/Vivado/2017.4/data/verilog/src/unisims -s glbl

include $(shell cocotb-config --makefiles)/Makefile.inc
include $(shell cocotb-config --makefiles)/Makefile.sim
