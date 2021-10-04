VERILOG_SOURCES = $(XILINX_VIVADO)/data/verilog/src/glbl.v sim_build/dut.v
TOPLEVEL=top
MODULE=tb_tagger
COMPILE_ARGS=-y$(XILINX_VIVADO)/data/verilog/src/unisims -s glbl

ROOT_DIR=$(PWD)/../../../..
DARTIQ_IMAGE=technosystem/dartiq:6.0

include $(shell cocotb-config --makefiles)/Makefile.sim

sim_build/dut.v: $(ROOT_DIR)/mcord_daq/gateware/cores/tagger.py $(ROOT_DIR)/mcord_daq/gateware/tests/tagger/tb_tagger.py
	mkdir -p sim_build
	dartiq run -m $(ROOT_DIR) -m $(ROOT_DIR)/modules/ELHEP_Cores --workspace=sim_build/ --image=$(DARTIQ_IMAGE) "python -m mcord_daq.gateware.cores.tagger"
