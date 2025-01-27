"""
Testbench for the Substitution Layer module.

This module tests the Substitution Layer module by comparing the
output of the Python implementation with the VHDL implementation.

@author: Timothée Charrier
"""

import os
import sys
from pathlib import Path

import cocotb
from cocotb.runner import Simulator, get_runner
from cocotb.triggers import Timer
from substitution_layer_model import (
    SubstitutionLayerModel,
)

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str(object=(Path(__file__).parent.parent.parent).resolve()))

from cocotb_utils import (
    get_dut_state,
    init_hierarchy,
    log_generics,
)

INIT_INPUTS = {
    "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=False),
}


def get_generics(dut: cocotb.handle.HierarchyObject) -> dict:
    """
    Retrieve the generic parameters from the DUT.

    Parameters
    ----------
    dut : object
        The device under test (DUT).

    Returns
    -------
    dict
        A dictionary containing the generic parameters.

    """
    return {
        "NUM_SBOXES": int(dut.NUM_SBOXES.value),
    }


async def initialize_dut(dut: cocotb.handle.HierarchyObject, inputs: dict) -> None:
    """
    Initialize the DUT with the given inputs.

    Parameters
    ----------
    dut : object
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
    dut : object
        The device under test (DUT).

    """
    try:
        # Get the generic parameters and Log them
        generics = get_generics(dut=dut)
        log_generics(dut=dut, generics=generics)

        # Define the model
        substitution_layer_model = SubstitutionLayerModel()

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS)

        # Assert the output
        substitution_layer_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
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
async def substitution_layer_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        # Define the model
        substitution_layer_model = SubstitutionLayerModel()

        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Test with specific inputs
        dut_inputs = {
            "i_state": [
                0x80400C0600000000,
                0x0001020304050607,
                0x08090A0B0C0D0EFF,
                0x0001020304050607,
                0x08090A0B0C0D0E0F,
            ],
        }

        # Set the inputs
        await initialize_dut(dut=dut, inputs=dut_inputs)

        # Update the model and assert the output
        substitution_layer_model.assert_output(dut=dut, inputs=dut_inputs)

        dut._log.info("Starting random tests...")

        # Try with random inputs
        for _ in range(10):
            # Generate random inputs
            new_inputs = {
                "i_state": init_hierarchy(dims=(5,), bitwidth=64, use_random=True),
            }

            # Set the inputs
            await initialize_dut(dut=dut, inputs=new_inputs)

            # Update and Assert the output
            substitution_layer_model.assert_output(dut=dut, inputs=new_inputs)

    except Exception as e:
        dut_state: dict = get_dut_state(dut=dut)
        formatted_dut_state: str = "\n".join(
            [f"{key}: {value}" for key, value in dut_state.items()],
        )
        error_message: str = (
            f"Failed in substitution_layer_test with error: {e}\n"
            f"DUT state at error:\n"
            f"{formatted_dut_state}"
        )
        raise RuntimeError(error_message) from e


def test_substitution_layer() -> None:
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
        f"{rtl_path}/substitution_layer/sbox.sv",
        f"{rtl_path}/substitution_layer/substitution_layer.sv",
    ]

    parameters: dict[str, int] = {
        "NUM_SBOXES": 64,
    }

    # Top-level HDL entity
    entity: str = "substitution_layer"

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
            parameters=parameters,
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
        error_message: str = f"Failed in test_xor_end with error: {e}"
        raise RuntimeError(error_message) from e


if __name__ == "__main__":
    test_substitution_layer()
