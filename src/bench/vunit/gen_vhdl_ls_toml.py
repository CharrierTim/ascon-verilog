"""Generate VHDL-LS configuration file for Rust HDL integration.

This script automates the creation of vhdl_ls.toml configuration required by VHDL Language Server.
While it provides a convenient alternative to manual configuration, note that manually optimized
configurations may yield better results in some environments. This script is particularly useful
when default configurations fail due to Python version mismatches or other environment-specific issues.

Usage:
    python gen_vhdl_ls_toml.py [VUnit arguments]
"""

from pathlib import Path

import toml
from vunit import VUnit
from vunit.ui.library import Library
from vunit.ui.source import SourceFileList


def gen_vhdl_db(vu, output_file):
    """Generate the toml file required by rust_hdl (vhdl_ls).

    Parameters
    ----------
    vu: :class:`vunit.VUnit`
        A VUnit object.
    output_file: :class:`pathlib.Path`
        A Path object pointing to the output file.s
    """
    libs = vu.get_libraries()
    vhdl_ls = {"libraries": {}}
    for lib in libs:
        vhdl_ls["libraries"].update({lib.name: {"files": [file.name for file in lib.get_source_files()]}})
    with open(output_file, "w") as f:
        toml.dump(vhdl_ls, f)


# Define the source and bench paths
SRC_ROOT: Path = Path(__file__).parent.parent.parent / "rtl" / "vhdl"
BENCH_ROOT: Path = Path(__file__).parent / "ascon" / "test"

# Define the libraries
src_library_name: str = "lib_rtl"
bench_library_name: str = "lib_bench"

# Initialize VUnit
VU: VUnit = VUnit.from_argv()
VU.add_vhdl_builtins()

# Add the source files to the library
LIB_SRC: Library = VU.add_library(library_name=src_library_name)
LIB_SRC.add_source_files(pattern=SRC_ROOT / "**" / "*.vhd")

# Add the test library
LIB_BENCH: SourceFileList = VU.add_library(library_name=bench_library_name)
LIB_BENCH.add_source_files(pattern=BENCH_ROOT / "*.vhd")

# Generate the VHDL database
gen_vhdl_db(VU, output_file="vhdl_ls.toml")
