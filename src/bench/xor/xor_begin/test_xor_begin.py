"""
Testbench for the XOR Begin Layer.

This module tests the XOR Begin Layer function module by comparing the
output of the Python implementation with the Verilog implementation.

Author: Timothée Charrier
"""

import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.runner import Simulator, get_runner
from cocotb.triggers import Timer
from xor_begin_model import XorBeginModel

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent.parent).resolve()))

from cocotb_utils import get_dut_state, init_hierarchy

INIT_INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
    "i_data": 0,
    "i_key": 0,
    "i_enable_xor_key": 0,
    "i_enable_xor_data": 0,
}


async def initialize_dut(dut: cocotb.handle.HierarchyObject, inputs: dict) -> None:
    """
    Initialize the DUT with the given inputs.

    Parameters
    ----------
    dut : SimHandleBase
        The device under test (DUT).
    inputs : dict
        The input dictionary.

    """
    for key, value in inputs.items():
        getattr(dut, key).value = value
    await Timer(time=10, units="ns")


@cocotb.test()
async def reset_dut_test(dut: cocotb.handle.HierarchyObject) -> None:
    """
    Test the DUT's behavior during reset.

    Verifies that the output is correctly reset and remains stable.

    Parameters
    ----------
    dut : SimHandleBase
        The device under test (DUT).

    """
    try:
        # Define the model
        xor_begin_model = XorBeginModel()

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS)

        # Verify the output
        xor_begin_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        dut_state = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            f"{key}: {value}" for key, value in dut_state.items()
        )
        error_message: str = (
            f"Failed in reset_dut_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


@cocotb.test()
async def xor_begin_test(dut: cocotb.handle.HierarchyObject) -> None:
    """
    Test the DUT's behavior during normal computation.

    Parameters
    ----------
    dut : SimHandleBase
        The device under test (DUT).

    """
    try:
        # Define the model
        xor_begin_model = XorBeginModel()

        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Test with specific inputs
        dut_inputs = [
            {
                "i_state": [0xFFFFFFFFFFFFFFFF] * 5,
                "i_data": 0xFFFFFFFFFFFFFFFF,
                "i_key": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                "i_enable_xor_key": 0,
                "i_enable_xor_data": 0,
            },
            {
                "i_state": [0xFFFFFFFFFFFFFFFF] * 5,
                "i_data": 0xFFFFFFFFFFFFFFFF,
                "i_key": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                "i_enable_xor_key": 1,
                "i_enable_xor_data": 0,
            },
            {
                "i_state": [0xFFFFFFFFFFFFFFFF] * 5,
                "i_data": 0xFFFFFFFFFFFFFFFF,
                "i_key": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                "i_enable_xor_key": 0,
                "i_enable_xor_data": 1,
            },
            {
                "i_state": [0xFFFFFFFFFFFFFFFF] * 5,
                "i_data": 0xFFFFFFFFFFFFFFFF,
                "i_key": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                "i_enable_xor_key": 1,
                "i_enable_xor_data": 1,
            },
        ]

        for inputs in dut_inputs:
            await initialize_dut(dut=dut, inputs=inputs)
            xor_begin_model.assert_output(dut=dut, inputs=inputs)

        # Test with random inputs
        for _ in range(10):
            random_inputs = {
                "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=True),
                "i_data": random.randint(0, 2**64 - 1),
                "i_key": random.randint(0, 2**128 - 1),
                "i_enable_xor_key": random.randint(0, 1),
                "i_enable_xor_data": random.randint(0, 1),
            }
            await initialize_dut(dut=dut, inputs=random_inputs)
            xor_begin_model.assert_output(dut=dut, inputs=random_inputs)

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            f"{key}: {value}" for key, value in dut_state.items()
        )
        error_message: str = (
            f"Failed in xor_begin_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_xor_begin() -> None:
    """Function Invoked by the test runner to execute the tests."""
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
        f"{rtl_path}/xor/xor_begin.sv",
    ]

    # Top-level HDL entity
    entity: str = "xor_begin"

    try:
        # Get simulator name from environment
        simulator: str = os.environ.get("SIM", default=default_simulator)

        # Initialize the test runner
        runner: Simulator = get_runner(simulator_name=simulator)

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
        error_message: str = f"Failed in test_xor_begin with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_xor_begin()
