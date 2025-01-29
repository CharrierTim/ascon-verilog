# Makefile for simulating Verilog code with cocotb and Verilator

# Directory containing Verilog source files
SRC_DIR             := ../../../rtl/example/

# Source Files
VERILOG_SOURCES     := $(SRC_DIR)/adder.sv

# Cocotb and Verilator configuration
SIM                 := verilator
TOPLEVEL_LANG       := verilog
TOPLEVEL            := adder
COCOTB_TEST_MODULES := test_adder
MODULE              := $(COCOTB_TEST_MODULES)
EXTRA_ARGS          += --trace --trace-fst --trace-structs -GDATA_WIDTH=8

# Calling cocotb
PWD                 := $(shell pwd)
export PYTHONPATH   := $(PWD)/../model:$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf results.xml __pycache__ sim_build dump.fst