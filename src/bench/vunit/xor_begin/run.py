"""
VUnit test runner for xor begin.

This module sets up the VUnit test environment, adds necessary source files,
and runs the tests for the xor begin implementation.
"""

import os
import sys
from pathlib import Path

from vunit import VUnit
from vunit.ui.library import Library
from vunit.ui.source import SourceFileList

# Define the simulation tool
VUNIT_SIMULATOR: str = "nvc"
os.environ["VUNIT_SIMULATOR"] = os.environ.get("VUNIT_SIMULATOR", default=VUNIT_SIMULATOR)

# Define the source and bench paths
SRC_ROOT: Path = Path(__file__).parent.parent.parent.parent / "rtl" / "vhdl"
BENCH_ROOT: Path = Path(__file__).parent / "test"

# Define the libraries
src_library_name: str = "lib_rtl"
bench_library_name: str = "lib_bench"

# Initialize VUnit
argv: list[str] = sys.argv if len(sys.argv) > 1 else ["-v", "-p", "0"]
VU: VUnit = VUnit.from_argv(argv=argv)
VU.add_vhdl_builtins()

# Add the source files to the library
LIB_SRC: Library = VU.add_library(library_name=src_library_name)
LIB_SRC.add_source_files(pattern=SRC_ROOT / "**" / "*.vhd")

# Add the test library
LIB_BENCH: SourceFileList = VU.add_library(library_name=bench_library_name)
LIB_BENCH.add_source_files(pattern=BENCH_ROOT / "*.vhd")

VU.set_sim_option(name="disable_ieee_warnings", value=True)
VU.main()
