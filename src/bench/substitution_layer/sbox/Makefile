# Makefile for simulating Verilog code with cocotb and Verilator

# Directory containing Verilog source files
SRC_DIR             := ../../../rtl

# Source Files
VERILOG_SOURCES     := $(SRC_DIR)/ascon_pkg.sv \
                    $(SRC_DIR)/substitution_layer/sbox.sv \

# Cocotb and Verilator configuration
SIM                 := verilator
TOPLEVEL_LANG       := verilog
TOPLEVEL            := sbox
COCOTB_TEST_MODULES := test_sbox
MODULE              := $(COCOTB_TEST_MODULES)
COMPILE_ARGS        += -j 0
EXTRA_ARGS          += --trace

# Calling cocotb
PWD                 := $(shell pwd)
export PYTHONPATH   := $(PWD)/../model:$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf results.xml __pycache__ sim_build dump.vcd