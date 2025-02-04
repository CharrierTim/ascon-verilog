#################################################
 ascon-verilog - Ascon implementation in Verilog
#################################################

**********
 Synopsis
**********

This project provides a synthesizable implementation of the Ascon 128
algorithm in Verilog, using open-source tools. The project is divided
into two main parts:

#. The ``src/rtl`` directory contains the Verilog modules for the Ascon
   128 algorithm.
#. The ``src/bench`` directory contains the python testbenches for the
   Ascon 128 algorithm.

This project is an improvement of a project I did during my studies at
the `École des Mines de Saint-Étienne
<https://www.mines-stetienne.fr/>`_.

**********************
 Open-source Software
**********************

This project relies entirely on open-source software for the development
and testing of hardware modules. The following tools are used:

Verilator
=========

`Verilator <https://github.com/verilator/verilator>`_ is a free software
Verilog/SystemVerilog simulator. Follow the instructions on the
`Verilator Guide <https://verilator.org/guide/latest/install.html>`_ to
install it or get the latest `oss-cad-suite release
<https://github.com/YosysHQ/oss-cad-suite-build/releases>`_ for easier
installation.

Surfer
======

`Surfer <https://surfer-project.org/>`_ is a waveform viewer used to
visualize simulation results (``*.vcd`` or ``*.fst`` files). I used a
VSCode workflow, so I used the `built-in extension
<https://marketplace.visualstudio.com/items?itemName=surfer-project.surfer>`_.
It can also be downloaded from the `Surfer Gitlab
<https://gitlab.com/surfer-project/surfer>`_ or alternatively use
`GTKWave <http://gtkwave.sourceforge.net/>`_.

Cocotb
======

`Cocotb <https://docs.cocotb.org/en/stable/#>`_ is a coroutine-based
co-simulation testbench environment for verifying
VHDL/Verilog/SystemVerilog RTL using Python. It is used to write
testbenches for the VHDL modules and run simulations. ``Pytest``
framework or ``make`` is used to run the tests.

lcov
====

`lcov <http://ltp.sourceforge.net/coverage/lcov.php>`_ is a tool used to
generate html coverage reports.

Ruff
====

`Ruff <https://github.com/astral-sh/ruff>`_ is a linter and formatter
for Python source code. It is used to ensure the code is clean and
readable.

*******
 Setup
*******

The flow of the project was tested on a Linux machine, but should work
on any operating system that supports the tools mentioned above.

#. Clone the repository using the following command:

      .. code:: bash

         git clone https://github.com/CharrierTim/ascon-verilog.git

#. Change the directory to the project folder:

      .. code:: bash

         cd ascon-verilog

#. Create a virtual environment using the following command:

      .. code:: bash

         python3 -m venv venv

#. Activate the virtual environment using the following command:

      .. code:: bash

         source venv/bin/activate

#. Install the Python dependencies using the following command:

      .. code:: bash

         pip install -r requirements.txt

#. Install Verilator following the instructions on the `Verilator Guide
   <https://verilator.org/guide/latest/install.html>`_. Project was
   tested with Verilator ``5.031`` (devel rev
   ``v5.030-153-gc7355b405``).

#. Install Surfer from the `Surfer Gitlab
   <https://gitlab.com/surfer-project/surfer>`_ or use `GTKWave
   <http://gtkwave.sourceforge.net/>`_.

#. Install lcov by either downloading the latest release from the `lcov
   repo <https://github.com/linux-test-project/lcov/releases>`_ or using
   the package manager of your operating system.

*******
 Usage
*******

To ensure all the tools are installed correctly, run the following
command at the root of the project:

.. code:: bash

   pytest

Or alternatively, use the ``make`` command in the ``src/bench``
directory:

.. code:: bash

   cd src/bench
   make
   make clean

Then, you can use VSCode build-in python extension to run specific test,
or ``your-python-interpreter path/to/test.py`` to run a specific test or
the ``make`` command in the specific test directory.

VSCode Workflow
===============

If you are using Visual Studio Code, this project includes a ``.vscode``
directory with preconfigured settings:

-  ``extensions.json`` - Lists recommended extensions for the project.

-  ``settings.json`` - Contains workspace-specific settings:

      -  Verible Language Server is used for linting and formatting.
      -  Ruff Python linter and formatter is used for Python files.
      -  Various other settings to improve the development experience.

**********
 Coverage
**********

To generate the coverage report, you need to run the "top level"
testbench, which is the ``test_ascon.py`` file in the
``src/bench/ascon`` directory. Both approach automatically generate the
coverage report, in the ``sim_build/coverage`` folder. The ``make``
approach just requires one more command: ``make coverage`` after the
``make`` command.

You can open the ``index.html`` file in your browser to see the coverage
report.

***********
 Synthesis
***********

Synthesis was only checked using Vivado, but we could use `Yosys
<https://github.com/YosysHQ/yosys>`_ to synthesize the design for a full
open-source flow.

**************
 Contribution
**************

Contributions are welcome! Please submit a pull request or open an issue
on GitHub.

*********
 License
*********

This project is licensed under the MIT License. See the ``LICENSE`` file
for details.
