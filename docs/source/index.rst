#############################
 ascon-verilog Documentation
#############################

.. image:: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-test.yml/badge.svg
   :target: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-test.yml
   :alt: Regression Tests

.. image:: https://github.com/CharrierTim/ascon-verilog/actions/workflows/build-deploy-docs.yml/badge.svg
   :target: https://github.com/CharrierTim/ascon-verilog/actions
   :alt: Documentation Status

**************
 Introduction
**************

This project provides a synthesizable implementation of the Ascon 128
algorithm in Verilog, using open-source tools. The project is divided
into two main parts:

#. The ``src/rtl`` directory contains the Verilog modules for the Ascon
   128 algorithm.
#. The ``src/bench`` directory contains the python testbenches for the
   Ascon 128 algorithm.

This project is an improvement of a project I did during my studies at
the `École des Mines de Saint-Étienne`_.

You can find a `Cocotb Presentation`_ at the root of the repository.

*******************
 Table of Contents
*******************

.. toctree::
   :maxdepth: 1
   :name: mastertoc

   files/getting_started
   files/ascon
   files/hdl_modules
   files/python_modules
   files/references

**************
 Installation
**************

To get started with the project, follow the installation instructions
provided in the `Getting Started`_ guide.

.. _cocotb presentation: https://github.com/CharrierTim/ascon-verilog/blob/master/cocotb-presentation.pdf

.. _getting started: https://charriertim.github.io/ascon-verilog/files/getting_started.html

.. _école des mines de saint-étienne: https://www.mines-stetienne.fr/
