"""
Testbench for the sbox module.

This module tests the sbox module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import cocotb
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner
from sbox_model import SboxModel

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent.parent).resolve()))

from cocotb_utils import get_dut_state

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject
    from cocotb_tools.runner import Runner

S_TABLE: list[int] = [
    0x04,
    0x0B,
    0x1F,
    0x14,
    0x1A,
    0x15,
    0x09,
    0x02,
    0x1B,
    0x05,
    0x08,
    0x12,
    0x1D,
    0x03,
    0x06,
    0x1C,
    0x1E,
    0x13,
    0x07,
    0x0E,
    0x00,
    0x0D,
    0x11,
    0x18,
    0x10,
    0x0C,
    0x01,
    0x19,
    0x16,
    0x0A,
    0x0F,
    0x17,
]


@cocotb.test()
async def reset_dut_test(dut: HierarchyObject) -> None:
    """
    Test the DUT's behavior during reset.

    Verifies that the output is correctly reset and remains stable.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Raises
    ------
    RuntimeError
        If the DUT fails to reset.

    """
    try:
        # Define the model
        sbox_model = SboxModel(s_table=S_TABLE)

        # Initialize the DUT
        dut.i_data.value = 0

        # Wait for few ns (combinatorial logic only in the DUT)
        await Timer(time=10, unit="ns")

        # Check the output
        sbox_output: int = sbox_model.compute(i_data=0)

        # Assert the output
        assert int(dut.o_data.value) == sbox_output

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in reset_dut_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


@cocotb.test()
async def sbox_test(dut: HierarchyObject) -> None:
    """
    Test the DUT's behavior during normal computation.

    Verifies that the output is correctly computed.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Raises
    ------
    RuntimeError
        If the DUT fails to compute the correct output.

    """
    try:
        # Define the model
        sbox_model = SboxModel(s_table=S_TABLE)

        # Initialize the DUT
        await reset_dut_test(dut=dut)

        # Loop through the test vectors
        for elem in S_TABLE:
            # Set the input data
            dut.i_data.value = elem

            # Wait for few ns (combinatorial logic only in the DUT)
            await Timer(time=10, unit="ns")

            # Check the output
            sbox_output: int = sbox_model.compute(i_data=elem)

            dut._log.info(
                "Input: 0x%02X, Unsigned Input: %d, "
                "Output: 0x%02X, Unsigned Output: %d",
                elem,
                elem,
                sbox_output,
                sbox_output,
            )

            # Assert the output
            assert int(dut.o_data.value) == sbox_output

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in sbox_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_sbox() -> None:
    """
    Function Invoked by the test runner to execute the tests.

    Raises
    ------
    RuntimeError
        If the test fails to build or run.

    """
    # Define the simulator to use
    default_simulator: str = "verilator"

    # Build Args
    build_args: list[str] = ["-j", "0", "-Wall"]

    # Define LIB_RTL
    library: str = "LIB_RTL"

    # Define rtl_path
    rtl_path: Path = (Path(__file__).parent.parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources: list[str] = [
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/substitution_layer/sbox.sv",
    ]

    # Top-level HDL entity
    entity: str = "sbox"

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_args=build_args,
            build_dir="sim_build",
            clean=True,
            hdl_library=library,
            hdl_toplevel=entity,
            sources=sources,
            verbose=True,
            waves=True,
        )

        # Run tests
        runner.test(
            build_dir="sim_build",
            hdl_toplevel=entity,
            hdl_toplevel_library=library,
            test_module=f"test_{entity}",
            verbose=True,
            waves=True,
        )

        # Log the wave file path
        wave_file: Path = (Path("sim_build") / "dump.vcd").resolve()
        sys.stdout.write(f"Wave file: {wave_file}\n")

    except Exception as e:
        error_message: str = f"Failed in test_sbox with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_sbox()
