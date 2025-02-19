#################
 Getting Started
#################

********************
 Installation guide
********************

Prerequisites
=============

Before you begin, ensure you have the following:

-  A Linux system or WSL installed on Windows

.. note::

   The project can work on Windows, but tools are usually easier to
   install on Linux. If you are using Windows, I recommend using WSL.

Setup WSL (Windows Users Only)
==============================

Install WSL with Ubuntu 24.04 in a PowerShell:

.. code:: powershell

   wsl --install -d Ubuntu-24.04

For more information, refer to the `WSL documentation`_.

Clone the Repository
====================

Open the Ubuntu terminal and clone the repository:

.. code:: bash

   git clone https://github.com/CharrierTim/ascon-verilog.git

Change to the project directory:

.. code:: bash

   cd ascon-verilog

Upgrade the System

.. code:: bash

   sudo apt update
   sudo apt upgrade

Install Verilator
=================

Verilator is the SystemVerilog Simulator used to compile and run the
testbenches. Install Verilator using one of the following methods:

#. Install Verilator from the Ubuntu repository:

   .. code:: bash

      sudo apt install verilator

#. Install Verilator from source (see `Verilator Installation Guide`_):

   .. code:: bash

      sudo apt-get install -y \
            git help2man perl python3 make autoconf g++ flex bison ccache \
            libgoogle-perftools-dev numactl perl-doc \
            libfl2 libfl-dev \
            zlib1g zlib1g-dev

      unset VERILATOR_ROOT
      git clone https://github.com/verilator/verilator.git
      cd verilator
      git checkout stable

      autoconf         # Create ./configure script
      ./configure      # Configure and create Makefile
      make -j `nproc`  # Build Verilator itself (if error, try just 'make')
      sudo make install

#. Download and install the latest OSS-CAD-Suite_ releases, which
   includes Verilator binaries:

   .. code:: bash

      # Example for the 2025-02-13 release
      wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2025-02-13/oss-cad-suite-linux-x64-20250213.tgz

      tar -xzf oss-cad-suite-linux-x64-20250213.tgz
      source oss-cad-suite/environment

.. note::

   **Verilator Version Information**

   -  The project was tested with Verilator 5.031
   -  Base version: v5.030
   -  Build revision: gc7355b405
   -  Minimum recommended version: 5.030

   If you encounter issues, ensure your Verilator version is up to date.

Install Python
==============

Python is used for running scripts and managing dependencies. Install
Python 3 and the required packages:

.. code:: bash

   sudo apt install python3 python3-pip python3-venv

Then, create a virtual environment and install the required packages:

.. code:: bash

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

Install lcov
============

lcov_ is used to generate code coverage reports. Install it with:

.. code:: bash

   sudo apt install lcov

********************
 Tools Informations
********************

This project relies entirely on open-source software for the development
and testing of hardware modules. The following tools are used:

Cocotb
======

Cocotb_ is a coroutine-based co-simulation testbench environment for
verifying VHDL/Verilog/SystemVerilog RTL using Python. It is used to
write testbenches for the VHDL modules and run simulations.

lcov
====

lcov_ is a tool used to generate html coverage reports.

Pytest
======

Pytest_ is a testing framework that makes it easy to write simple tests
and scales to support complex functional testing for applications and
libraries.

Surfer
======

Most testbenches generate a ``*.vcd`` file that can be visualized using
a waveform viewer.

Surfer_ is a waveform viewer used to visualize simulation results
(``*.vcd`` or ``*.fst`` files). I used a VSCode workflow, so I used the
`Surfer VSCode Extension`_. It can also be downloaded from the `Surfer
Gitlab`_ or alternatively use GTKWave_.

Ruff
====

Ruff_ is a linter and formatter for Python source code. It is used to
ensure the code is clean and readable.

Verible
=======

Verible_ is a suite of SystemVerilog tools that includes a linter and
formatter. I used it as a linter and formatter for the SystemVerilog
code. The tool is not required to run the project. The formatting rules
are defined in the ``.vscode/settings.json`` file. If you want to use
it, you can install the `Verible VSCode Extension`_.

.. note::

   My VSCode recommended extensions can be found in the
   ``.vscode/extensions.json`` file.

Verilator
=========

Verilator_ is a free software Verilog/SystemVerilog simulator.

.. _cocotb: https://docs.cocotb.org/en/stable/#>

.. _gtkwave: http://gtkwave.sourceforge.net/

.. _lcov: https://github.com/linux-test-project/lcov

.. _oss-cad-suite: https://github.com/YosysHQ/oss-cad-suite-build/releases

.. _pytest: https://docs.pytest.org/en/stable/

.. _ruff: <https://github.com/astral-sh/ruff

.. _surfer: https://surfer-project.org/

.. _surfer gitlab: https://gitlab.com/surfer-project/surfer

.. _surfer vscode extension: https://marketplace.visualstudio.com/items?itemName=surfer-project.surfer

.. _verible: https://github.com/chipsalliance/verible

.. _verible vscode extension: https://marketplace.visualstudio.com/items?itemName=chipsalliance.verible

.. _verilator: https://github.com/verilator/verilator

.. _verilator installation guide: https://verilator.org/guide/latest/install.html

.. _wsl documentation: https://docs.microsoft.com/en-us/windows/wsl/install
