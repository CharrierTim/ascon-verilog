"""Library for utility functions used in the testbenches.

@author: Timothée Charrier
"""

from __future__ import annotations

import random
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from tabulate import tabulate

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Array

if TYPE_CHECKING:
    from pathlib import Path

    from cocotb.handle import HierarchyObject


def random_signed_value(bitwidth: int) -> int:
    """Generate a random signed value within the given bitwidth.

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
    """Initialize a hierarchical data structure (1D, 2D, 3D, etc.).

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
    *,
    clock_name: str = "clock",
    period_ns: int = 10,
    verbose: bool = True,
) -> None:
    """Initialize and start the clock for the DUT.

    Parameters
    ----------
    dut : HierarchyObject
        The Device Under Test (DUT).
    clock_name : str, optional
        Name of the clock signal (default is "clock").
    period_ns : int
        Clock period in nanoseconds (default is 10).
    verbose : bool, optional
        If True, logs the clock operation (default is True).

    Raises
    ------
    AttributeError
        If the clock signal is not found in the DUT.
    RuntimeError
        If there is an error setting up the clock.
    """
    # Check if the DUT has a clock signal
    if not hasattr(dut, clock_name):
        error_message: str = f"Failed to find clock signal: {clock_name}"
        raise AttributeError(error_message)

    try:
        clock = Clock(signal=getattr(dut, clock_name), period=period_ns, unit="ns")
        await cocotb.start(clock.start(start_high=False))

        if not verbose:
            return

        dut._log.info(f"Clock {clock_name} started with period {period_ns} ns.")

    except Exception as e:
        error_message: str = (
            f"Failed in setup_clock with error: {e}",
            "Hint: DUT might not have a clock signal.",
        )
        raise RuntimeError(error_message) from e


async def reset_dut(
    dut: HierarchyObject,
    *,
    clock_name: str = "clock",
    reset_name: str = "reset_n",
    num_cycles: int = 5,
    reset_high: int = 0,
    verbose: bool = True,
) -> None:
    """Reset the DUT.

    This function asserts the reset signal for 'num_cycles' and then deasserts it.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test.
    clock_name : str, optional
        Name of the clock signal (default is "clock").
    reset_name : str, optional
        Name of the reset signal (default is "reset_n").
    num_cycles : int, optional
        Number of clock cycles to assert the reset signal (default is 5).
    reset_high : int, optional
        Indicates if the reset signal is active high (1) or active low (0).
        By default, the reset signal is active low (0).
    verbose : bool, optional
        If True, logs the reset operation (default is True).

    Raises
    ------
    ValueError
        If the reset_high value is not 0 or 1.
    AttributeError
        If the clock or reset signal is not found in the DUT.
    RuntimeError
        If there is an error resetting the DUT.
    """
    # Check if the reset_high value is valid
    if reset_high not in [0, 1]:
        error_message: str = (
            f"Invalid reset_high value: {reset_high}",
            "Hint: reset_high should be 0 or 1.",
        )
        raise ValueError(error_message)

    # Check if the DUT has a clock signal
    if not hasattr(dut, clock_name):
        error_message = f"Clock signal {clock_name} not found in DUT."
        raise AttributeError(error_message)

    # Check if the DUT has a reset signal
    if not hasattr(dut, reset_name):
        error_message = f"Reset signal {reset_name} not found in DUT."
        raise AttributeError(error_message)

    try:
        # Assert reset (based on active level)
        getattr(dut, reset_name).value = reset_high
        await ClockCycles(signal=getattr(dut, clock_name), num_cycles=num_cycles)

        # Deassert reset
        getattr(dut, reset_name).value = 1 - reset_high
        await ClockCycles(signal=getattr(dut, clock_name), num_cycles=2)

        if not verbose:
            return

        reset_type = "active high" if reset_high == 1 else "active low"
        dut._log.info(
            f"DUT reset with {reset_name} signal ({reset_type}for {num_cycles} cycles.",
        )

    except Exception as e:
        error_message: str = f"Failed in reset_dut with error: {e}."
        raise RuntimeError(error_message) from e


async def sys_enable_dut(
    dut: HierarchyObject,
    *,
    clock_name: str = "clock",
    sys_enable_name: str = "i_sys_enable",
    verbose: bool = True,
) -> None:
    """Enable the DUT.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test.
    clock_name : str, optional
        Name of the clock signal (default is "clock").
    sys_enable_name : str, optional
        Name of the sys_enable signal (default is "i_sys_enable").
    verbose : bool, optional
        If True, logs the enable operation (default is True).

    Raises
    ------
    AttributeError
        If the sys_enable or clock signal is not found in the DUT.
    AttributeError
        If the DUT does not have a sys_enable signal.
    RuntimeError
        If there is an error enabling the DUT.
    """
    # Check if the DUT has a sys_enable signal
    if not hasattr(dut, sys_enable_name):
        error_message: str = f"Failed to find sys_enable signal: {sys_enable_name}"
        raise AttributeError(error_message)

    # Check if the DUT has a clock signal
    if not hasattr(dut, clock_name):
        error_message: str = f"Failed to find clock signal: {clock_name}"
        raise AttributeError(error_message)

    try:
        getattr(dut, sys_enable_name).value = 1
        await getattr(dut, clock_name).rising_edge

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
    clock_name: str = "clock",
    reset_name: str = "reset_n",
    sys_enable_name: str = "i_sys_enable",
    clock_period_ns: int = 10,
    reset_high: int = 0,
    verbose: bool = True,
) -> None:
    """Initialize the DUT with default values.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    inputs : dict
        A dictionary containing the input names and values.
    outputs : dict
        A dictionary containing the output names and expected values.
    clock_name : str, optional
        Name of the clock signal (default is "clock").
    reset_name : str, optional
        Name of the reset signal (default is "reset_n").
    sys_enable_name : str, optional
        Name of the sys_enable signal (default is "i_sys_enable").
    clock_period_ns : int, optional
        Clock period in nanoseconds (default is 10).
    reset_high : int, optional
        Indicates if the reset signal is active high (1) or active low (0).
        By default, the reset signal is active low (0).
    verbose : bool, optional
        If True, logs the initialization operation (default is True).

    Raises
    ------
    RuntimeError
        If there is an error initializing the DUT.

    Examples
    --------
    >>> inputs = {"i_data": 0, "i_valid": 0}
    >>> outputs = {"o_data": 0, "o_valid": 0}
    >>> await initialize_dut(dut, inputs, outputs)
    """
    try:
        # Setup the clock
        await setup_clock(
            dut=dut,
            clock_name=clock_name,
            period_ns=clock_period_ns,
            verbose=verbose,
        )

        # Reset the DUT
        await reset_dut(
            dut=dut,
            clock_name=clock_name,
            reset_name=reset_name,
            reset_high=reset_high,
            verbose=verbose,
        )

        # Set the input values
        for key, value in inputs.items():
            getattr(dut, key).value = value

        # Wait a few clock cycles
        await ClockCycles(signal=getattr(dut, clock_name), num_cycles=2)

        # Check the output values
        for key, value in outputs.items():
            assert getattr(dut, key).value == value, f"Output {key} is incorrect"

        # Check if i_sys_enable is present
        if hasattr(dut, sys_enable_name):
            await sys_enable_dut(
                dut=dut,
                clock_name=clock_name,
                sys_enable_name=sys_enable_name,
                verbose=verbose,
            )

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
    clock_name: str = "clock",
    verbose: bool = True,
) -> None:
    """Toggle a signal between high and low values.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).
    signal_dict : dict
        A dictionary containing the signal name and value.
        If the value is 1, the signal is toggled to 0; otherwise, it is toggled to 1.
    clock_name : str, optional
        Name of the clock signal (default is "clock").
    verbose : bool, optional
        If True, logs the signal toggling operation (default is True).

    Raises
    ------
    AttributeError
        If the clock signal or required signal is not found in the DUT.
    AttributeError
        If the DUT does not have the required signal in the signal_dict.
    RuntimeError
        If there is an error toggling the signal.

    Examples
    --------
    >>> signal_dict = {"i_valid": 0, "i_ready": 0}
    >>> await toggle_signal(dut, signal_dict, clock_name="clock", verbose=True)
    """
    # Check if the DUT has a clock signal
    if not hasattr(dut, clock_name):
        error_message: str = f"Failed to find clock signal: {clock_name}"
        raise AttributeError(error_message)

    # Check if the DUT has the required signals
    for key, value in signal_dict.items():
        if not hasattr(dut, key):
            error_message: str = f"Failed to find signal: {key} in DUT."
            raise AttributeError(error_message)

        try:
            # Set initial value
            getattr(dut, key).value = value
            await getattr(dut, clock_name).rising_edge

            # Toggle to opposite value
            getattr(dut, key).value = 0 if value == 1 else 1
            await getattr(dut, clock_name).rising_edge

        except Exception as e:
            error_message: str = f"Failed to toggle signal {key}. Error: {e}"
            raise RuntimeError(error_message) from e

    # Log success message if verbose
    if verbose:
        dut._log.info("Signal toggled successfully.")


def log_generics(dut: HierarchyObject, generics: dict[str, int]) -> None:
    """Log the generic parameters from the DUT in a table format.

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
    """Get the state of the DUT at a given time.

    Parameters
    ----------
    dut : HierarchyObject
        The device under test (DUT).

    Returns
    -------
    state : dict
        The state of the DUT ports.

    Raises
    ------
    RuntimeError
        If there is an error getting the value of a port.

    Examples
    --------
    >>> state = get_dut_state(dut)
    >>> print(state)
    """
    state = {}
    for attr in dut._sub_handles:
        if attr.startswith(("i_", "o_")):
            try:
                value = getattr(dut, attr).value
                value = tuple(hex(x) for x in value) if isinstance(value, Array) else hex(int(value))
                state[attr] = value
            except (TypeError, ValueError) as e:
                error_message: str = f"Failed to get the value of {attr}.\nError: {e}"
                raise RuntimeError(error_message) from e
    return state


def generate_coverage_report_verilator(dat_file: Path, output_folder: Path) -> None:
    """Generate the coverage report.

    This function generates the coverage report using the verilator_coverage
    and genhtml commands. The coverage report is stored in the output_folder/coverage
    directory. Just open the index.html file in a browser to view the report.

    Parameters
    ----------
    dat_file : Path
        The path to the coverage.dat file.
    output_folder : Path
        The simulation build directory

    Raises
    ------
    FileNotFoundError
        If the genhtml executable is not found in the PATH.
    SystemExit
        If the coverage report generation fails.
    """
    # Check if the vcover executable is available
    genhtml_path: str | None = shutil.which(cmd="genhtml")
    if not genhtml_path:
        error_message: str = (
            "Hint: Make sure that genhtml is installed on your system.\n"
            "If not, you can install it using the following command:\n"
            "sudo apt-get install lcov"
        )
        raise FileNotFoundError(error_message)

    # Create the output folder if it does not exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # Define the commands as argument lists
    command_coverage: list[str] = [
        "verilator_coverage",
        "-write-info",
        f"{output_folder}/coverage.info",
        str(object=dat_file),
    ]
    command_genhtml: list[str] = [
        "genhtml",
        f"{output_folder}/coverage.info",
        "--output-directory",
        f"{output_folder}",
    ]

    try:
        # Run the commands
        subprocess.run(
            args=command_coverage,
            check=True,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        subprocess.run(
            args=command_genhtml,
            check=True,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )

        # Log the coverage report path
        sys.stdout.write(f"{' '.join(command_coverage)}\n")
        sys.stdout.write(f"{' '.join(command_genhtml)}\n")
        sys.stdout.write(f"Coverage report generated in {output_folder}\n")

    except Exception as e:
        error_message: str = f"Failed to generate the coverage report with error: {e}\n"
        raise SystemExit(error_message) from e


def generate_coverage_report_questa(ucdb_file: Path, output_folder: Path) -> None:
    """Generate the coverage report in HTML format.

    Parameters
    ----------
    ucdb_file : Path
        The path to the UCDB file.
    output_folder : Path
        The path to the output folder.

    Raises
    ------
    FileNotFoundError
        If the vcover executable is not found in the PATH.
    RuntimeError
        If the coverage report generation fails.
    """
    # Check if the vcover executable is available
    vcover_path: str | None = shutil.which(cmd="vcover")
    if not vcover_path:
        error_message: str = "vcover executable not found in PATH"
        raise FileNotFoundError(error_message)

    # Create the output folder if it does not exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # Define the command to generate the coverage report
    vcover_cmd: list[str] = [
        vcover_path,
        "report",
        "-annotate",
        "-codeAll",
        "-details",
        "-html",
        "-output",
        str(object=output_folder),
        str(object=ucdb_file),
    ]

    try:
        subprocess.run(
            args=vcover_cmd,
            check=True,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )

        sys.stdout.write(f"{' '.join(vcover_cmd)}\n")
        sys.stdout.write(f"Coverage report generated in {output_folder}\n")

    except subprocess.CalledProcessError as e:
        error_message: str = f"Failed to generate coverage report with error: {e}"
        raise RuntimeError(error_message) from e
