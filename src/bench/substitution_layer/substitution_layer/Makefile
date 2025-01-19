# Makefile for simulating VHDL code with verilator and cocotb

# Directory containing VHDL source files
SRC_DIR             := ../../rtl

# VHDL Source Files
VERILOG_SOURCES     := $(SRC_DIR)/ascon_pkg.v \
                    $(SRC_DIR)/adder_const/adder_const.v

# Cocotb and nvc flags
SIM                 := verilator
TOPLEVEL_LANG       := verilog
TOPLEVEL            := adder_const
COCOTB_TEST_MODULES := test_adder_const
SIM_ARGS            := --trace

# Calling cocotb
PWD                 := $(shell pwd)
export PYTHONPATH   := $(PWD)/../model:$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf $(LIB) $(WAVE_FILE) results.xml __pycache__ sim_build
