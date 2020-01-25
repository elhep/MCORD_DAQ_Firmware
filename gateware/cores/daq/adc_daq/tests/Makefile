VERILOG_SOURCES = $(XILINX_VIVADO)/data/verilog/src/glbl.v $(PWD)/adc_phy_daq.v
TOPLEVEL=top
MODULE=tb_adc_phy_daq

COMPILE_ARGS=-y$(XILINX_VIVADO)/data/verilog/src/unisims -s glbl

include $(shell cocotb-config --makefiles)/Makefile.inc
include $(shell cocotb-config --makefiles)/Makefile.sim
