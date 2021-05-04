VERILOG_SOURCES=$(XILINX_VIVADO)/data/verilog/src/glbl.v sim_build/dut.v
TOPLEVEL=top
TOPLEVEL_LANG=verilog
MODULE=tb_trigger_controller
SIM=icarus
WAVES=1
PROJECT_ROOT=../../../..

include $(shell cocotb-config --makefiles)/Makefile.sim

OUTDIR=$(PWD)/sim_build

sim_build/dut.v: $(PWD)/../trigger_controller.py
	mkdir -p $(OUTDIR)
	(cd $(PROJECT_ROOT); dartiq run --workspace=$(OUTDIR) "python -m mcord_daq.gateware.trigger_controller.trigger_controller")
