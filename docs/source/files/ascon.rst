######################
 Ascon Implementation
######################

This page contains some details about the SystemVerilog implementation
of Ascon128.

Most of the information is taken from the **Ascon-based lightweight
cryptography standards for constrained devices** report :cite:`FIPS800-232`.

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

**********
 Glossary
**********

.. list-table::
   :widths: 25 75
   :header-rows: 1

   -  -  Term
      -  Definition

   -  -  **Ascon128**
      -  A lightweight cryptographic algorithm designed for constrained
         environments, providing both encryption and authentication.

   -  -  **Data Path** (:math:`S`)

      -  The width of the data processed in parallel within the hardware
         implementation. For Ascon128, it is 320 bits, which is
         represented as a 5x64-bit words, :math:`S = (S_0, S_1, S_2,
         S_3, S_4)`.

   -  -  **Round** (:math:`r`)
      -  A single iteration of the cryptographic algorithm's internal
         transformation. Ascon128 processes one round per clock cycle.

   -  -  **Key** (:math:`K`)
      -  The secret value used for encryption and decryption. In
         Ascon128, the key size is 128 bits.

   -  -  **Nonce** (:math:`N`)

      -  A unique value used only once for each encryption operation to
         ensure the same plaintext encrypts to different ciphertexts
         each time.

   -  -  **Plaintext** (:math:`P`)
      -  The original data that is to be encrypted.

   -  -  **Ciphertext** (:math:`C`)
      -  The encrypted data produced from the plaintext using the
         encryption algorithm.

   -  -  **Tag** (:math:`T`)
      -  The authentication tag generated during encryption, used to
         verify the integrity and authenticity of the ciphertext.

   -  -  **Permutation** (:math:`p^r`)
      -  A cryptographic transformation applied to the state of the
         algorithm, consisting of multiple rounds.

   -  -  **State**
      -  The internal representation of data within the algorithm, which
         is transformed during each round of the permutation.

The inputs to the Ascon128 algorithm are the plaintext, key, nonce and
associated data. The algorithm produces the ciphertext and tag as
outputs.

************
 Background
************

Permutation :math:`p^6` and :math:`p^{12}`
==========================================

The core of Ascon128's cryptographic strength lies in its permutation
functions :math:`p^6` and :math:`p^{12}`. These functions transform the
320-bit state :math:`S` through three sequential stages:

#. **Constant Addition Layer** (:math:`p_C`): Adds round-specific
   constants to ensure uniqueness per round.
#. **Substitution Layer** (:math:`p_S`): Applies non-linear S-box
   operations to provide confusion.
#. **Linear Diffusion Layer** (:math:`p_L`): Ensures thorough mixing of
   bits for diffusion.

The complete permutation can be expressed as:

.. math::
   :label: ascon-permutation

   p(S) = p_L \circ p_S \circ p_C
   \text{ where }
   \begin{cases}
   p_L: \text{Linear diffusion layer providing bit mixing} \\
   p_S: \text{Non-linear substitution using 5-bit S-boxes} \\
   p_C: \text{Round constant addition for uniqueness}
   \end{cases}

The Constant-Addition Layer :math:`p_C`
=======================================

The constant addition layer :math:`p_C` is responsible for adding
round-specific constants to the state. It performs the following

.. math::
   :label: ascon-constant-addition

   S_2 \leftarrow S_2 \oplus c_r

The constant :math:`c_r` is defined as:

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

   -  -  Round r of :math:`p^{12}`
      -  Round r of :math:`p^6`
      -  Constant :math:`c_r`

   -  -  0
      -
      -  000000000000000000f0

   -  -  1
      -
      -  000000000000000000e1

   -  -  2
      -
      -  000000000000000000d2

   -  -  3
      -
      -  000000000000000000c3

   -  -  4
      -
      -  000000000000000000b4

   -  -  5
      -
      -  000000000000000000a5

   -  -  6
      -  0
      -  00000000000000000096

   -  -  7
      -  1
      -  00000000000000000087

   -  -  8
      -  2
      -  00000000000000000078

   -  -  9
      -  3
      -  00000000000000000069

   -  -  10
      -  4
      -  0000000000000000005a

   -  -  11
      -  5
      -  0000000000000000004b

The Substitution Layer :math:`p_S`
==================================

The substitution layer 𝑝 updates 𝑆 the state S with 64 parallel
applications of the 5-bit substitution box SBOX using a lookup table.
The substitution layer can be expressed as:

.. math::
   :label: ascon-substitution

   S_i \leftarrow SBOX(S_i) \quad \forall i \in \{0, 1, 2, 3, 4\}

It applies the S-box to each of the 64-bit words in the state, in
column-wise fashion.

Here is the definition of the S-box lookup table:

.. list-table::
   :header-rows: 1
   :widths: 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10

   -  -  x
      -  00
      -  01
      -  02
      -  03
      -  04
      -  05
      -  06
      -  07
      -  08
      -  09
      -  0a
      -  0b
      -  0c
      -  0d
      -  0e
      -  0f

   -  -  SBOX(x)
      -  4
      -  b
      -  1f
      -  14
      -  1a
      -  15
      -  9
      -  2
      -  1b
      -  5
      -  8
      -  12
      -  1d
      -  3
      -  6
      -  1c

.. list-table::
   :header-rows: 1
   :widths: 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10

   -  -  x
      -  10
      -  11
      -  12
      -  13
      -  14
      -  15
      -  16
      -  17
      -  18
      -  19
      -  1a
      -  1b
      -  1c
      -  1d
      -  1e
      -  1f

   -  -  SBOX(x)
      -  1e
      -  13
      -  7
      -  e
      -  0
      -  d
      -  11
      -  18
      -  10
      -  c
      -  1
      -  19
      -  16
      -  a
      -  f
      -  17

Note that 5-bit inputs are represented in hexadecimal, (e.g., 𝑥 =1
corresponds to (0, 0, 0, 0, 1)).

The Linear Diffusion Layer :math:`p_L`
======================================

The linear diffusion layer :math:`p_L` provides diffusion within each
64-bit word of the state. It is defined as:

.. math::
   :label: ascon-linear-diffusion

   S_i \leftarrow \Sigma_{i}^{} S_i \text{ for } i \in \{0, 1, 2, 3, 4\}

Where each :math:`\Sigma_{i}^{} S_i` is defined as:

.. math::
   :label: ascon-linear-diffusion-sum

   \begin{aligned}
   \Sigma_{2}(S_2) &= S_2 \oplus (S_2 \gg \phantom{0}1)  \oplus (S_2 \gg \phantom{0}6)  \\
   \Sigma_{1}(S_1) &= S_1 \oplus (S_1 \gg 61) \oplus (S_1 \gg 39) \\
   \Sigma_{2}(S_2) &= S_2 \oplus (S_2 \gg \phantom{0}1)  \oplus (S_2 \gg \phantom{0}6)  \\
   \Sigma_{3}(S_3) &= S_3 \oplus (S_3 \gg 10) \oplus (S_3 \gg 17) \\
   \Sigma_{4}(S_4) &= S_4 \oplus (S_4 \gg \phantom{0}7)  \oplus (S_4 \gg 41)
   \end{aligned}

Let's note that :math:`\gg` denotes a cyclic rotation to the right.
