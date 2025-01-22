SIM?=ghdl
TOPLEVEL_LANG=vhdl
PROJ_HOME?=../..
WORK_BASE?=../..

TOPLEVEL = dut
MODULE = test_${TOPLEVEL}

VHDL_SOURCES+=\
    ${PROJ_HOME}/tests/rtl/rgb2dvi/DVI_Constants.vhd        \
    ${PROJ_HOME}/tests/rtl/rgb2dvi/SyncAsync.vhd        \
    ${PROJ_HOME}/tests/rtl/rgb2dvi/SyncAsyncReset.vhd        \
    ${PROJ_HOME}/tests/rtl/rgb2dvi/TMDS_Encoder.vhd \
    ${PROJ_HOME}/tests/rtl/rgb2dvi/OutputSERDES.vhd \
    ${PROJ_HOME}/tests/rtl/rgb2dvi/ClockGen.vhd \
    ${PROJ_HOME}/tests/rtl/rgb2dvi/rgb2dvi.vhd \

COCOTB_SOURCES = \
    ./dut.vhd

COMPILE_ARGS+=-fsynopsys -fexplicit 
COMPILE_ARGS+=-Whide 

include ${WORK_BASE}/rtlflo/cocotb_helper.mak

xx:
	@echo ${VHDL_SOURCES}
