"""
Library for utility functions used in the testbenches.

@author: Timothée Charrier
"""

from __future__ import annotations

import os
import random
import shutil
import sys
import time

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from tabulate import tabulate

# Define error messages
ERRORS = {
    "MISSING_BITWIDTH": ("Bitwidth is missing or not specified."),
    "MISSING_SIGNAL": (
        "Failed to assert reset state. The DUT may not have the required signals."
    ),
    "MISSING_CLOCK": (
        "Failed to start the clock. The DUT may not have a clock signal."
    ),
    "MISSING_RESET": ("Failed to reset the DUT. The DUT may not have a reset signal."),
    "MISSING_SYS_ENABLE": (
        "Failed to enable the DUT. The DUT may not have a system enable signal."
    ),
    "FAILED_INIT": (
        "Failed to initialize the DUT. "
        "Please check the initialization parameters and DUT configuration."
    ),
    "FAILED_RESET": (
        "Failed to reset the DUT."
        "Please ensure the reset signal is correctly configured."
    ),
    "FAILED_ENABLE": (
        "Failed to enable the DUT."
        "Please ensure the enable signal is correctly configured."
    ),
    "FAILED_CLOCK": (
        "Failed to start the clock."
        "Please check the clock configuration and DUT clock signal."
    ),
    "FAILED_SETUP": (
        "Failed to setup the DUT."
        "Please verify the setup parameters and DUT configuration."
    ),
    "FAILED_COMPILATION": (
        "Failed to compile the design."
        "Please check the design files and compilation settings."
    ),
    "FAILED_SIMULATION": (
        "Failed to run the simulation."
        "Please check the simulation environment and settings."
    ),
    "INVALID_BITWIDTH": (
        "Invalid bitwidth. Please ensure the bitwidth is a positive integer."
    ),
    "INVALID_CONFIGURATION": (
        "Invalid configuration. Please review the configuration parameters."
    ),
    "INVALID_RESET_VALUE": (
        "Invalid reset value. Please ensure the reset value is either 0 or 1."
    ),
    "INVALID_STATE": (
        "Invalid signal. Please ensure the signal is correctly configured."
    ),
}

# Define progress bar thresholds
PROGRESS_BAR_LOW = 33
PROGRESS_BAR_HIGH = 66


def random_signed_value(bitwidth: int) -> int:
    """
    Generate a random signed value within the given bitwidth.

    Parameters
    ----------
    bitwidth : int
        The bitwidth of the signed value.

    Returns
    -------
    int
        A random signed integer within the range of the given bitwidth.

    Raises
    ------
    ValueError
        If the bitwidth is not a positive integer.

    """
    if not isinstance(bitwidth, int) or bitwidth <= 0:
        raise ValueError(ERRORS["INVALID_BITWIDTH"])

    max_val = (1 << (bitwidth - 1)) - 1
    min_val = -(1 << (bitwidth - 1))
    return random.randint(min_val, max_val)


def init_hierarchy(
    dims: tuple[int, ...],
    *,
    bitwidth: int | None = None,
    use_random: bool = False,
) -> list:
    """
    Initialize a hierarchical data structure (1D, 2D, 3D, etc.).

    Parameters
    ----------
    dims : tuple[int, ...]
        Dimensions of the hierarchical structure (e.g., (4, 3, 2)).
    bitwidth : int, optional
        Bitwidth for random signed values.
    use_random : bool, optional
        If True, initialize with random values; otherwise, fill with zeroes.

    Returns
    -------
    list
        Hierarchical structure filled as specified.

    """
    if not dims:
        return random_signed_value(bitwidth) if use_random else 0

    return [
        init_hierarchy(
            dims=dims[1:],
            bitwidth=bitwidth,
            use_random=use_random,
        )
        for _ in range(dims[0])
    ]


async def setup_clock(
    dut: cocotb.handle.HierarchyObject,
    period_ns: int = 10,
    *,
    verbose: bool = True,
) -> None:
    """
    Initialize and start the clock for the DUT.

    Parameters
    ----------
    dut : cocotb.handle.HierarchyObject
        The Device Under Test (DUT).
    period_ns : int
        Clock period in nanoseconds (default is 10).
    verbose : bool, optional
        If True, logs the clock operation (default is True).

    """
    try:
        clock = Clock(signal=dut.clock, period=period_ns, units="ns")
        await cocotb.start(clock.start(start_high=False))

        if not verbose:
            return

        dut._log.info(f"Clock started with period {period_ns} ns.")

    except AttributeError:
        raise RuntimeError(ERRORS["MISSING_CLOCK"]) from None


async def reset_dut(
    dut: cocotb.handle.HierarchyObject,
    num_cycles: int = 5,
    *,
    reset_high: int = 0,
    verbose: bool = True,
) -> None:
    """
    Reset the DUT.

    This function assumes the reset signal is active low.
    It asserts the reset signal for 'num_cycles' and then deasserts it.

    Parameters
    ----------
    dut : cocotb.handle.HierarchyObject
        The device under test.
    num_cycles : int, optional
        Number of clock cycles to assert the reset signal (default is 5).
    reset_high : int, optional
        Indicates if the reset signal is active high (1) or active low (0).
        By default, the reset signal is active low (0).
    verbose : bool, optional
        If True, logs the reset operation (default is True).

    """
    if reset_high not in [0, 1]:
        raise ValueError(ERRORS["INVALID_RESET_VALUE"])

    try:
        if reset_high == 0:
            dut.reset_n.value = 0
        else:
            dut.reset_h.value = 1

        await ClockCycles(dut.clock, num_cycles)

        if reset_high == 0:
            dut.reset_n.value = 1
        else:
            dut.reset_h.value = 0

        await ClockCycles(dut.clock, 2)

        if verbose:
            dut._log.info(
                f"DUT reset for {num_cycles} cycles with reset_high={reset_high}.",
            )

    except AttributeError as e:
        raise RuntimeError(ERRORS["MISSING_RESET"]) from e


async def sys_enable_dut(
    dut: cocotb.handle.HierarchyObject,
    *,
    verbose: bool = True,
) -> None:
    """
    Enable the DUT.

    Parameters
    ----------
    dut : object
        The device under test.
    verbose : bool, optional
        If True, logs the enable operation (default is True).

    """
    try:
        dut.i_sys_enable.value = 1
        await RisingEdge(signal=dut.clock)

        if not verbose:
            return

        dut._log.info("DUT enabled.")

    except AttributeError as e:
        raise RuntimeError(ERRORS["MISSING_SYS_ENABLE"]) from e


async def initialize_dut(
    dut: cocotb.handle.HierarchyObject,
    inputs: dict,
    outputs: dict,
    *,
    clock_period_ns: int = 10,
    reset_high: int = 0,
) -> None:
    """
    Initialize the DUT with default values.

    Parameters
    ----------
    dut : object
        The device under test (DUT).
    inputs : dict
        A dictionary containing the input names and values.
    outputs : dict
        A dictionary containing the output names and expected values.
    clock_period_ns : int, optional
        Clock period in nanoseconds (default is 10).
    reset_high : int, optional
        Indicates if the reset signal is active high (1) or active low (0).
        By default, the reset signal is active low (0).

    Usage
    -----

    >>> inputs = {"i_data": 0, "i_valid": 0}
    >>> outputs = {"o_data": 0, "o_valid": 0}
    >>> await initialize_dut(dut, inputs, outputs)

    """
    try:
        # Setup the clock
        await setup_clock(dut=dut, period_ns=clock_period_ns)

        # Reset the DUT
        await reset_dut(dut=dut, verbose=True, reset_high=reset_high)

        # Set the input values
        for key, value in inputs.items():
            getattr(dut, key).value = value

        # Wait a few clock cycles
        await ClockCycles(signal=dut.clock, num_cycles=5)

        # Check the output values
        for key, value in outputs.items():
            assert getattr(dut, key).value == value, f"Output {key} is incorrect"

        # Check if i_sys_enable is present
        if hasattr(dut, "i_sys_enable"):
            await sys_enable_dut(dut=dut, verbose=True)
            await ClockCycles(signal=dut.clock, num_cycles=5)

        dut._log.info("DUT initialized successfully.")

    except Exception as e:
        raise RuntimeError(ERRORS["FAILED_INIT"]).format(e=e) from e


async def toggle_signal(
    dut: cocotb.handle.HierarchyObject,
    signal_dict: dict,
    *,
    verbose: bool = True,
) -> None:
    """
    Toggle a signal between high and low values.

    Parameters
    ----------
    dut : object
        The device under test (DUT).
    signal_dict : dict
        A dictionary containing the signal name and value.
        If the value is 1, the signal is toggled to 0; otherwise, it is toggled to 1.
    verbose : bool, optional
        If True, logs the signal toggling operation (default is True).

    Usage
    -----

    >>> signal_dict = {"i_valid": 0, "i_ready": 0}
    >>> await toggle_signal(dut, signal_dict)

    """
    try:
        for key, value in signal_dict.items():
            getattr(dut, key).value = value
            await RisingEdge(signal=dut.clock)

            if value == 1:
                getattr(dut, key).value = 0
            else:
                getattr(dut, key).value = 1

            await RisingEdge(signal=dut.clock)

        if verbose:
            dut._log.info("Signal toggled successfully.")

    except AttributeError as e:
        raise RuntimeError(ERRORS["MISSING_SIGNAL"]) from e


def log_generics(dut: cocotb.handle.HierarchyObject, generics: dict[str, int]) -> None:
    """
    Log the generic parameters from the DUT in a table format.

    Parameters
    ----------
    dut : object
        The device under test (DUT).
    generics : dict
        A dictionary of generic parameters.

    """
    table = tabulate(generics.items(), headers=["Parameter", "Value"], tablefmt="grid")
    dut._log.info(f"Running with generics:\n{table}")
