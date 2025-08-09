Getting Started
===============

This project provides two equivalent implementations of the ASCON-128 algorithm. Choose
the implementation that best fits your needs:

- **SystemVerilog Flow**: Uses Verilator simulator with Cocotb testbenches
- **VHDL Flow**: Uses NVC simulator with VUnit testbenches

.. note::

    You can install both flows if you want to compare implementations or work with both
    HDLs.

Common Prerequisites
--------------------

Before you begin, ensure you have the following:

- A Linux system or WSL installed on Windows

.. note::

    The project can work on Windows, but tools are usually easier to install on Linux.
    If you are using Windows, I recommend using WSL.

Setup WSL (Windows Users Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install WSL with Ubuntu 24.04 in a PowerShell:

.. code-block:: powershell

    wsl --install -d Ubuntu-24.04

For more information, refer to the `WSL documentation`_.

Clone the Repository
~~~~~~~~~~~~~~~~~~~~

Open the Ubuntu terminal and clone the repository:

.. code-block:: bash

    git clone https://github.com/CharrierTim/ascon-verilog.git

Change to the project directory:

.. code-block:: bash

    cd ascon-verilog

Upgrade the System:

.. code-block:: bash

    sudo apt update
    sudo apt upgrade

Install Python
~~~~~~~~~~~~~~

Python is used for running scripts and managing dependencies for both flows:

.. code-block:: bash

    sudo apt install python3 python3-pip python3-venv

Create a virtual environment and install the required packages:

.. code-block:: bash

    python3 -m venv .venv
    source .venv/bin/activate
    pip install .

This will install dependencies for both flows including Cocotb, VUnit, Ruff, and other
testing tools.

If you want to install the documentation dependencies you can do so with:

.. code-block:: bash

    pip install -e ".[docs]"

SystemVerilog Flow
------------------

Choose this flow if you want to work with the SystemVerilog implementation.

Install Verilator
~~~~~~~~~~~~~~~~~

.. note::

    **Verilator Version Information**

    - The project was tested with Verilator 5.031
    - Base version: v5.030
    - Build revision: gc7355b405
    - Minimum recommended version: 5.030

    If you encounter issues, ensure your Verilator version is up to date.

Verilator is the SystemVerilog simulator used to compile and run the testbenches. Choose
one of the following methods to install Verilator:

OSS CAD Suite (Recommended)
+++++++++++++++++++++++++++

Download and install the latest OSS-CAD-Suite_ release, which includes Verilator and
other useful tools:

.. code-block:: bash

    # Example for the 2025-02-13 release
    wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2025-02-13/oss-cad-suite-linux-x64-20250213.tgz
    tar -xzf oss-cad-suite-linux-x64-20250213.tgz
    source oss-cad-suite/environment

Build from Source
+++++++++++++++++

For the latest version, you can build Verilator from source (see `Verilator Installation
Guide`_):

.. code-block:: bash

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

Ubuntu Repository (Not Recommended)
+++++++++++++++++++++++++++++++++++

The version in Ubuntu's repository might be outdated:

.. code-block:: bash

    sudo apt install verilator

Running SystemVerilog Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test the SystemVerilog implementation with Cocotb:

.. code-block:: bash

    # Run all SystemVerilog tests
    cd src/bench/cocotb
    make

    # Run specific module tests
    cd src/bench/cocotb/ascon
    make

VHDL Flow
---------

Choose this flow if you want to work with the VHDL implementation. If you want to use
GHDL, you can use the one provided in the OSS-CAD-Suite. Otherwise, you can use NVC.

Install NVC (VHDL Simulator)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NVC_ is a free open-source VHDL simulator that supports VHDL-93, VHDL-2002, VHDL-2008,
and VHDL-2019.

OSS CAD Suite (Recommended)
+++++++++++++++++++++++++++

NVC is included in the OSS-CAD-Suite. If you haven't installed it yet:

.. code-block:: bash

    # Example for the 2025-02-13 release
    wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2025-02-13/oss-cad-suite-linux-x64-20250213.tgz
    tar -xzf oss-cad-suite-linux-x64-20250213.tgz
    source oss-cad-suite/environment

Build from Source
+++++++++++++++++

For the latest version, you can build NVC from source:

.. code-block:: bash

    sudo apt-get install -y \
          build-essential autotools-dev automake autoconf \
          flex bison check llvm-dev pkg-config zlib1g-dev \
          libdw-dev libffi-dev libzstd-dev

    git clone https://github.com/nickg/nvc.git
    cd nvc
    ./autogen.sh
    mkdir build && cd build
    ../configure
    make
    sudo make install

Ubuntu Repository
+++++++++++++++++

.. code-block:: bash

    sudo apt install nvc

Running VHDL Tests
~~~~~~~~~~~~~~~~~~

Test the VHDL implementation with VUnit:

.. code-block:: bash

    # Run all VHDL tests
    python src/bench/vunit/test_ascon_modules.py

    # Run specific module tests
    cd src/bench/vunit/ascon
    python run.py

Optional Tools
--------------

Install lcov (Code Coverage)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

lcov_ is used to generate code coverage reports for SystemVerilog flow only:

.. code-block:: bash

    sudo apt install lcov

Tools Information
-----------------

This project supports both SystemVerilog and VHDL implementations of the ASCON-128
encryption algorithm. Each flow uses different tools optimized for the respective HDL.

SystemVerilog Flow Tools
~~~~~~~~~~~~~~~~~~~~~~~~

Verilator
+++++++++

Verilator_ is a free software Verilog/SystemVerilog simulator used for the SystemVerilog
implementation.

Cocotb
++++++

Cocotb_ is a coroutine-based co-simulation testbench environment for verifying
VHDL/Verilog/SystemVerilog RTL using Python. It is used to write testbenches for the
SystemVerilog modules and run simulations.

Verible
+++++++

Verible_ is a suite of SystemVerilog tools that includes a linter and formatter. I used
it as a linter and formatter for the SystemVerilog code. The tool is not required to run
the project. The formatting rules are defined in the ``.vscode/settings.json`` file. If
you want to use it, you can install the `Verible VSCode Extension`_.

VHDL Flow Tools
~~~~~~~~~~~~~~~

NVC
+++

NVC_ is a free open-source VHDL simulator that supports VHDL-93, VHDL-2002, VHDL-2008,
and VHDL-2019. It's used for simulating the VHDL implementation of the ASCON modules.
NVC provides excellent performance and supports modern VHDL features.

VUnit
+++++

VUnit_ is an open-source unit testing framework for VHDL/SystemVerilog. It's used to
write and run unit tests for the VHDL modules. VUnit provides features like test
discovery, automatic test runner generation, and comprehensive test reporting.

Common Tools
~~~~~~~~~~~~

These tools are used across both flows:

Ruff
++++

Ruff_ is a linter and formatter for Python source code. It is used to ensure the code is
clean and readable for both Cocotb and VUnit testbenches.

Pytest
++++++

Pytest_ is a testing framework that makes it easy to write simple tests and scales to
support complex functional testing for applications and libraries.

lcov
++++

lcov_ is a tool used to generate HTML coverage reports for both SystemVerilog and VHDL
flows.

Surfer
++++++

Most testbenches generate a ``*.vcd`` or ``*.fst`` file that can be visualized using a
waveform viewer.

Surfer_ is a waveform viewer used to visualize simulation results (``*.vcd`` or
``*.fst`` files). I used a VSCode workflow, so I used the `Surfer VSCode Extension`_. It
can also be downloaded from the `Surfer Gitlab`_ or alternatively use GTKWave_.

.. note::

    My VSCode recommended extensions can be found in the ``.vscode/extensions.json``
    file.

.. _cocotb: https://docs.cocotb.org/en/stable/#>

.. _gtkwave: http://gtkwave.sourceforge.net/

.. _lcov: https://github.com/linux-test-project/lcov

.. _nvc: https://github.com/nickg/nvc

.. _oss-cad-suite: https://github.com/YosysHQ/oss-cad-suite-build/releases

.. _pytest: https://docs.pytest.org/en/stable/

.. _ruff: https://github.com/astral-sh/ruff

.. _surfer: https://surfer-project.org/

.. _surfer gitlab: https://gitlab.com/surfer-project/surfer

.. _surfer vscode extension: https://marketplace.visualstudio.com/items?itemName=surfer-project.surfer

.. _verible: https://github.com/chipsalliance/verible

.. _verible vscode extension: https://marketplace.visualstudio.com/items?itemName=chipsalliance.verible

.. _verilator: https://github.com/verilator/verilator

.. _verilator installation guide: https://verilator.org/guide/latest/install.html

.. _vunit: https://vunit.github.io/

.. _wsl documentation: https://docs.microsoft.com/en-us/windows/wsl/install
