"""Vunit Test Suite."""

import sys
import unittest
from os import environ
from pathlib import Path
from subprocess import call
from sys import executable

from vunit.sim_if.common import has_simulator

ROOT: Path = Path(__file__).resolve().parent


@unittest.skipUnless(condition=has_simulator(), reason="Requires simulator")
class TestExternalRunScripts(unittest.TestCase):
    """Test that installation works."""

    def setUp(self) -> None:
        """Set up the test case."""
        print("\n::group::Log")
        sys.stdout.flush()

    def tearDown(self) -> None:
        """Tear down the test case."""
        print("\n::endgroup::")
        sys.stdout.flush()

    def test_addition_layer(self) -> None:
        """Test addition layer."""
        self.check(folder="addition_layer")

    def test_diffusion_layer(self) -> None:
        """Test diffusion layer."""
        self.check(folder="diffusion_layer")

    def test_substitution_layer(self) -> None:
        """Test substitution layer."""
        self.check(folder="substitution_layer")

    def test_xor_begin(self) -> None:
        """Test XOR begin."""
        self.check(folder="xor_begin")

    def test_xor_end(self) -> None:
        """Test XOR end."""
        self.check(folder="xor_end")

    def test_ascon(self) -> None:
        """Test the ascon top."""
        self.check(folder="ascon")

    def check(self, folder, args=None, vhdl_standard="2008", exit_code=0):
        """Run external run file and verify exit code."""
        new_env: dict[str, str] = environ.copy()
        new_env["VUNIT_VHDL_STANDARD"] = vhdl_standard
        run_file = ROOT / folder / "run.py"
        self.output_path = run_file.parent / "vunit_out"
        self.assertEqual(
            call(
                [
                    executable,
                    run_file,
                    "--clean",
                    f"--output-path={self.output_path}",
                ]
                + (args if args is not None else []),
                env=new_env,
            ),
            exit_code,
        )
