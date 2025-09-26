SIM?=ghdl
TOPLEVEL_LANG=vhdl
PROJ_HOME?=..
WORK_BASE?=../..

TOPLEVEL = tmds_encoder
MODULE = test_tmds


VHDL_SOURCES+=     ${WORK_BASE}/tests/rtl/rgb2dvi/TMDS_Encoder.vhd 
VHDL_SOURCES+=     ${WORK_BASE}/tests/rtl/rgb2dvi/DVI_Constants.vhd 

COMPILE_ARGS+=-fsynopsys -fexplicit
COMPILE_ARGS+=-Whide

include ${WORK_BASE}/rtlflo/cocotb_helper.mak

xx:
	@echo ${VHDL_SOURCES}
