library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity dut is
  port (
      PixelClk : in std_logic;
      SerialClk : in std_logic;
      vid_in_vsync : in std_logic;
      vid_in_hsync : in std_logic;
      vid_in_de    : in std_logic;
      vid_in_data  : in std_logic_vector(23 downto 0);
      vid_out_vsync : out std_logic;
      vid_out_hsync : out std_logic;
      vid_out_de    : out std_logic;
      vid_out_data  : out std_logic_vector(23 downto 0);
      tmds_in_clk_p  : in std_logic;
      tmds_in_clk_n  : in std_logic;
      tmds_in_data_p : in std_logic_vector(2 downto 0);
      tmds_in_data_n : in std_logic_vector(2 downto 0);
      tmds_out_clk_p  : out std_logic;
      tmds_out_clk_n  : out std_logic;
      tmds_out_data_p : out std_logic_vector(2 downto 0);
      tmds_out_data_n : out std_logic_vector(2 downto 0)
  );
end entity; 

architecture tb of dut is

begin

vid_out_data  <= vid_in_data ;
vid_out_de    <= vid_in_de   ;
vid_out_hsync <= vid_in_hsync;
vid_out_vsync <= vid_in_vsync;

tmds_out_clk_p  <= tmds_in_clk_p ;
tmds_out_clk_n  <= tmds_in_clk_n ;
tmds_out_data_p <= tmds_in_data_p;
tmds_out_data_n <= tmds_in_data_n;
end;
