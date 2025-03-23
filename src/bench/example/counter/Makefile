# Makefile for simulating Verilog code with cocotb and Verilator

# Directory containing Verilog source files
SRC_DIR             := ../../../rtl/example/

# Source Files
VERILOG_SOURCES     := $(SRC_DIR)/counter.sv

# Cocotb and Verilator configuration
SIM                 := verilator
TOPLEVEL_LANG       := verilog
TOPLEVEL            := counter
COCOTB_TEST_MODULES := test_counter
MODULE              := $(COCOTB_TEST_MODULES)
EXTRA_ARGS          += -Wall --trace --trace-fst --trace-structs -GG_DATA_WIDTH=8 
EXTRA_ARGS          += -GG_COUNT_FROM=3 -GG_COUNT_TO=47 -GG_STEP=1

# Calling cocotb
PWD                 := $(shell pwd)
export PYTHONPATH   := $(PWD)/../model:$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf results.xml __pycache__ sim_build