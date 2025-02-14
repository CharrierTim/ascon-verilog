"""
Library for utility functions used in the testbenches.

@author: Timothée Charrier
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Array
from tabulate import tabulate

if TYPE_CHECKING:
    from cocotb.handle import HierarchyObject


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
        error_message: str = (
            f"Invalid bitwidth: {bitwidth}",
            "Hint: bitwidth should be a positive integer.",
        )
        raise ValueError(error_message)

    max_val: int = (1 << (bitwidth - 1)) - 1
    min_val: int = -(1 << (bitwidth - 1))
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
        return random_signed_value(bitwidth=bitwidth) if use_random else 0

    return [
        init_hierarchy(
            dims=dims[1:],
            bitwidth=bitwidth,
            use_random=use_random,
        )
        for _ in range(dims[0])
    ]


async def setup_clock(
    dut: HierarchyObject,
    period_ns: int = 10,
    *,
    verbose: bool = True,
) -> None:
    """
    Initialize and start the clock for the DUT.

    Parameters
    ----------
    dut : HierarchyObject
        The Device Under Test (DUT).
    period_ns : int
        Clock period in nanoseconds (default is 10).
    verbose : bool, optional
        If True, logs the clock operation (default is True).

    """
    try:
        clock = Clock(signal=dut.clock, period=period_ns, unit="ns")
        await cocotb.start(clock.start(start_high=False))

        if not verbose:
            return

        dut._log.info(f"Clock started with period {period_ns} ns.")

    except Exception as e:
        error_message: str = (
            f"Failed in setup_clock with error: {e}",
            "Hint: DUT might not have a clock signal.",
        )
        raise RuntimeError(error_message) from e


async def reset_dut(
    dut: HierarchyObject,
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
    dut : HierarchyObject
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
        error_message: str = (
            f"Invalid reset_high value: {reset_high}",
            "Hint: reset_high should be 0 or 1.",
        )
        raise ValueError(error_message)

    try:
        if reset_high == 0:
            dut.reset_n.value = 0
        else:
            dut.reset_h.value = 1

        await ClockCycles(signal=dut.clock, num_cycles=num_cycles)

        if reset_high == 0:
            dut.reset_n.value = 1
        else:
            dut.reset_h.value = 0

        await ClockCycles(signal=dut.clock, num_cycles=2)

        if not verbose:
            return

        dut._log.info(
            f"DUT reset for {num_cycles} cycles with reset_high={reset_high}.",
        )

    except Exception as e:
        error_message: str = (
            f"Failed in reset_dut with error: {e}",
            "Hint: DUT might not have reset_n or reset_h port.",
        )
        raise RuntimeError(error_message) from e


async def sys_enable_dut(
    dut: HierarchyObject,
    *,
    verbose: bool = True,
) -> None:
    """
    Enable the DUT.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test.
    verbose : bool, optional
        If True, logs the enable operation (default is True).

    """
    try:
        dut.i_sys_enable.value = 1
        await dut.clock.rising_edge

        if not verbose:
            return

        dut._log.info("DUT enabled.")

    except Exception as e:
        error_message: str = (
            f"Failed in sys_enable_dut with error: {e}",
            "Hint: DUT might not have i_sys_enable port or clock signal.",
        )
        raise RuntimeError(error_message) from e


async def initialize_dut(
    dut: HierarchyObject,
    inputs: dict,
    outputs: dict,
    *,
    clock_period_ns: int = 10,
    reset_high: int = 0,
    verbose: bool = True,
) -> None:
    """
    Initialize the DUT with default values.

    Parameters
    ----------
    dut : HierarchyObject
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
    verbose : bool, optional
        If True, logs the initialization operation (default is True).

    Usage
    -----
    >>> inputs = {"i_data": 0, "i_valid": 0}
    >>> outputs = {"o_data": 0, "o_valid": 0}
    >>> await initialize_dut(dut, inputs, outputs)

    """
    try:
        # Setup the clock
        await setup_clock(dut=dut, period_ns=clock_period_ns, verbose=verbose)

        # Reset the DUT
        await reset_dut(dut=dut, reset_high=reset_high, verbose=verbose)

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
            await sys_enable_dut(dut=dut, verbose=verbose)
            await ClockCycles(signal=dut.clock, num_cycles=5)

        if not verbose:
            return

        dut._log.info("DUT initialized successfully.")

    except Exception as e:
        error_message: str = f"Failed in initialize_dut with error: {e}"
        raise RuntimeError(error_message) from e


async def toggle_signal(
    dut: HierarchyObject,
    signal_dict: dict,
    *,
    verbose: bool = True,
) -> None:
    """
    Toggle a signal between high and low values.

    Parameters
    ----------
    dut : HierarchyObject
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
            await dut.clock.rising_edge

            if value == 1:
                getattr(dut, key).value = 0
            else:
                getattr(dut, key).value = 1

            await dut.clock.rising_edge

        if not verbose:
            return

        dut._log.info("Signal toggled successfully.")

    except Exception as e:
        error_message: str = (
            f"Failed to toggle signal {key}.",
            f"Error: {e}",
        )
        raise RuntimeError(error_message) from e


def log_generics(dut: HierarchyObject, generics: dict[str, int]) -> None:
    """
    Log the generic parameters from the DUT in a table format.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    generics : dict
        A dictionary of generic parameters.

    """
    table: str = tabulate(
        tabular_data=generics.items(),
        headers=["Parameter", "Value"],
        tablefmt="grid",
    )
    dut._log.info(f"Running with generics:\n{table}")


def get_dut_state(dut: HierarchyObject) -> dict:
    """
    Get the state of the DUT at a given time.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Returns
    -------
    state : dict
        The state of the DUT ports.

    """
    state = {}
    for attr in dut._sub_handles:
        if attr.startswith(("i_", "o_")):
            try:
                value = getattr(dut, attr).value
                if isinstance(value, Array):
                    value = tuple(hex(x) for x in value)
                else:
                    value = hex(int(value))
                state[attr] = value
            except (TypeError, ValueError) as e:
                error_message: str = f"Failed to get the value of {attr}.\nError: {e}"
                raise RuntimeError(error_message) from e
    return state
