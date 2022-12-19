-- Counter from zero to 3

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;

LIBRARY LIB_RTL;
USE LIB_RTL.ascon_pack.ALL;
ENTITY compteur_simple_init IS

  PORT (
    clock_i : IN STD_LOGIC;
    resetb_i : IN STD_LOGIC;
    en_i : IN STD_LOGIC;
    init_a_i : IN STD_LOGIC;
    cpt_o : OUT STD_LOGIC_VECTOR(1 DOWNTO 0)
  );

END ENTITY compteur_simple_init;

ARCHITECTURE compteur_simple_init_arch OF compteur_simple_init IS

  SIGNAL cpt_s : INTEGER RANGE 0 TO 3;

BEGIN -- architecture compteur_simple_init_arch
  seq_0 : PROCESS (clock_i, resetb_i, en_i, init_a_i) IS
  BEGIN -- process seq_0
    IF (resetb_i = '0') THEN -- asynchronous reset (active low)
      cpt_s <= 0;
    ELSIF (clock_i'event AND clock_i = '1') THEN -- rising clock edge
      IF (en_i = '1') THEN
        IF (init_a_i = '1') THEN
          cpt_s <= 0;
        ELSE
          cpt_s <= cpt_s + 1;
        END IF;
      ELSE
        cpt_s <= cpt_s;

      END IF;
    END IF;
  END PROCESS seq_0;

  cpt_o <= std_logic_vector(to_unsigned(cpt_s, 2));
END ARCHITECTURE compteur_simple_init_arch;