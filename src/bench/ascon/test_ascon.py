"""
Testbench for the XOR Begin Layer.

This module tests the XOR Begin Layer function module by comparing the
output of the Python implementation with the verilog implementation.

@author: Timothée Charrier
"""

import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import ClockCycles

# Add the directory containing the utils.py file to the Python path
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))

from ascon_utils import (
    PermutationModel,
)
from cocotb_utils import (
    ERRORS,
    init_hierarchy,
    initialize_dut,
    toggle_signal,
)

INIT_INPUTS = {
    "i_start": 0,
    "i_data_valid": 0,
    "i_data": 0x0000000000000000,
    "i_key": 0x00000000000000000000000000000000,
    "i_nonce": 0x00000000000000000000000000000000,
}


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
        # Define the model
        _ = 1
        # permutation_model = PermutationModel(
        #     inputs=INIT_INPUTS,
        # )

        # Initialize the DUT
        await initialize_dut(dut=dut, inputs=INIT_INPUTS, outputs={})

        # # Update and Assert the output
        # permutation_model.assert_output(dut=dut, inputs=INIT_INPUTS)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_RESET"].format(e=e)) from e


@cocotb.test()
async def permutation_test(dut: cocotb.handle.HierarchyObject) -> None:
    """Test the DUT's behavior during normal computation."""
    try:
        _ = 1

        # Reset the DUT
        await reset_dut_test(dut=dut)

        # Define the ASCON inputs
        inputs = {
            "i_sys_enable": 1,
            "i_start": 0,
            "i_data_valid": 0,
            "i_data": 0x80400C0600000000,
            "i_key": 0x000102030405060708090A0B0C0D0E0F,
            "i_nonce": 0x000102030405060708090A0B0C0D0E0F,
        }

        # Set the inputs
        for key, value in inputs.items():
            dut.__getattr__(key).value = value

        # Wait for few clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=10)

        # Send the start signal
        await toggle_signal(dut=dut, signal_dict={"i_start": 1})

        # Wait for 12 clock cycles (1 permutation with 12 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=12)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x3230323280000000

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1})

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x446576656C6F7070

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1})

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x657A204153434F4E

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1})

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x20656E206C616E67

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1})

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # Update i_data
        dut.i_data.value = 0x6167652056484480

        # Set i_data_valid to 1
        await toggle_signal(dut=dut, signal_dict={"i_data_valid": 1})

        # Wait for 6 clock cycles (1 permutation with 6 rounds)
        await ClockCycles(signal=dut.clock, num_cycles=6)

        # Wait for a random number of clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=random.randint(0, 15))

        # We should enter in the final phase
        await ClockCycles(signal=dut.clock, num_cycles=12)

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_COMPUTATION"].format(e=e)) from e


def test_permutation() -> None:
    """Function Invoked by the test runner to execute the tests."""
    # Define the simulator to use
    default_simulator = "verilator"

    # Define LIB_RTL
    library = "LIB_RTL"

    # Define rtl_path
    rtl_path = (Path(__file__).parent.parent.parent / "rtl/").resolve()

    # Define the sources
    sources = [
        f"{rtl_path}/ascon_pkg.sv",
        f"{rtl_path}/add_layer/add_layer.sv",
        f"{rtl_path}/substitution_layer/sbox.sv",
        f"{rtl_path}/substitution_layer/substitution_layer.sv",
        f"{rtl_path}/diffusion_layer/diffusion_layer.sv",
        f"{rtl_path}/xor/xor_begin.sv",
        f"{rtl_path}/xor/xor_end.sv",
        f"{rtl_path}/permutation/permutation.sv",
        f"{rtl_path}/fsm/ascon_fsm.sv",
        f"{rtl_path}/ascon/ascon.sv",
    ]

    # Top-level HDL entity
    entity = "ascon"

    try:
        # Get simulator name from environment
        simulator = os.environ.get("SIM", default_simulator)

        # Initialize the test runner
        runner = get_runner(simulator_name=simulator)

        # Build HDL sources
        runner.build(
            build_args=[
                "-j",
                "0",
            ],
            build_dir="sim_build",
            clean=False,
            hdl_library=library,
            hdl_toplevel=entity,
            sources=sources,
            waves=True,
        )

        # Run tests
        runner.test(
            build_dir="sim_build",
            hdl_toplevel=entity,
            hdl_toplevel_library=library,
            test_module=f"test_{entity}",
            waves=True,
        )

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_COMPILATION"].format(e=e)) from e


if __name__ == "__main__":
    test_permutation()
