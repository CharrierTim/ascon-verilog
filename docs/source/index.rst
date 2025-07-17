ascon-verilog Documentation
===========================

.. image:: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-test.yml/badge.svg
    :target: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-test.yml
    :alt: Regression Tests

.. image:: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-deploy-docs.yml/badge.svg
    :target: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-deploy-docs.yml
    :alt: Documentation Status

Introduction
------------

This project provides synthesizable implementations of the Ascon 128 algorithm in both
SystemVerilog and VHDL, using open-source tools. You can choose between two equivalent
implementations:

- **SystemVerilog implementation**: Complete RTL design tested using Cocotb-based
  testbenches
- **VHDL implementation**: Functionally equivalent RTL design tested using VUnit-based
  testbenches

The project is organized as follows:

1. The ``src/rtl`` directory contains both SystemVerilog and VHDL modules for the Ascon
   128 algorithm.
2. The ``src/bench`` directory contains the verification environments: Cocotb
   testbenches for SystemVerilog modules and VUnit testbenches for VHDL modules.

This project is an improvement of a project I did during my studies at the `École des
Mines de Saint-Étienne`_.

You can find a `Cocotb Presentation`_ at the root of the repository.

Table of Contents
~~~~~~~~~~~~~~~~~

.. toctree::
    :maxdepth: 1
    :name: mastertoc

    files/getting_started
    files/ascon
    files/hdl_modules
    files/python_modules
    files/references

Installation
~~~~~~~~~~~~

To get started with the project, follow the installation instructions provided in the
`Getting Started`_ guide.

.. _cocotb presentation: https://github.com/CharrierTim/ascon-verilog/blob/master/cocotb-presentation.pdf

.. _getting started: https://charriertim.github.io/ascon-verilog/files/getting_started.html

.. _école des mines de saint-étienne: https://www.mines-stetienne.fr/
