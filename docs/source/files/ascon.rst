######################
 Ascon Implementation
######################

This page contains some details about the SystemVerilog implementation
of Ascon128.

**************
 Architecture
**************

The main goal of this project is to provide a synthesizable
implementation of the Ascon128 algorithm for data encryption.

Key features of the current implementation:

-  **320-bit data-path**: The design uses a 320-bit wide data path.
-  **1 round per cycle**: The hardware implementation processes one
   round of the algorithm per clock cycle.

***************
 Block Diagram
***************

.. image:: ../_static/ascon/ascon128-block-diagram.svg
   :align: center
   :width: 100%
   :alt: Ascon128 Block Diagram
   :target: ../_static/ascon/ascon128-block-diagram.svg
