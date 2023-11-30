SIM?=icarus
TOPLEVEL_LANG=verilog
#XILINX_BASE=${HOME}/projects/XilinxUnisimLibrary
#XILINX_BASE=${XILINX_VIVADO}/data
WORK_BASE?=../..
PROJ_HOME?=../..
COMPILE_LIBS?=${PROJ_HOME}/libs
#COMPILE_LIBS?=`readlink -f ${PROJ_HOME}/libs`
RTLFLO_PATH?=${PROJ_HOME}/rtlflo
CDSLIB?=./cds_${SIM}.lib

# DUT?=dut
TOPLEVEL?=dut
TEST?=${TOPLEVEL}_001
MODULE?=test_${TEST}


# IMPORT_SOURCES += \
#     ${PROJ_HOME}/tests/gowin_tb/driver/video_gen.v            \
#     ${PROJ_HOME}/tests/gowin_tb/driver/video_syntime_config.v \
#     ${PROJ_HOME}/tests/gowin_tb/driver/video_gen_syn.v        \
#     ${PROJ_HOME}/tests/gowin_tb/driver/video_gen_data.v       \
#     ${PROJ_HOME}/tests/gowin_tb/driver/driver.sv \
# 
# GOWIN_SOURCES += \
#    ${PROJ_HOME}/tests/gowin_project/src/dvi_tx/dvi_tx_vo.v

# VHDL_LIB_ORDER += \
#     UNISIM
# 
# VHDL_SOURCES_UNISIM += \
#     /opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/vhdl/src/unisims/unisim_VPKG.vhd \
#     /opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/vhdl/src/unisims/unisim_VCOMP.vhd \
# 	/opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/vhdl/src/unisims/primitive/IBUFDS.vhd \
# 	/opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/vhdl/src/unisims/primitive/IDELAYE2.vhd \
# 	/opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/vhdl/src/unisims/secureip/ISERDESE2.vhd \
# 
# VHDL_SOURCES += \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/DVI_Constants.vhd  \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/SyncAsync.vhd      \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/SyncAsyncReset.vhd \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/SyncBase.vhd       \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/InputSERDES.vhd    \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/GlitchFilter.vhd   \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/TWI_SlaveCtl.vhd   \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/PhaseAlign.vhd     \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/ChannelBond.vhd    \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/TMDS_Decoder.vhd   \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/TMDS_Clocking.vhd  \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/ResyncToBUFG.vhd   \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/EEPROM_8b.vhd      \
#     ${PROJ_HOME}/tests/digilent-dvi2rgb/src/dvi2rgb.vhd        \
#     ${PROJ_HOME}/tests/digilent-rgb2dvi/src/TMDS_Encoder.vhd   \
#     ${PROJ_HOME}/tests/digilent-rgb2dvi/src/OutputSERDES.vhd   \
#     ${PROJ_HOME}/tests/digilent-rgb2dvi/src/ClockGen.vhd       \
#     ${PROJ_HOME}/tests/digilent-rgb2dvi/src/rgb2dvi.vhd

# VHDL_SOURCES += \
#     ${PROJ_HOME}/tests/dvi/${TEST}.vhd
  
    
#RTL_SOURCES += \

DUT_SOURCES = \
    ${PROJ_HOME}/tests/dvi/vcd_dump.sv \
    ${PROJ_HOME}/tests/dvi/${TEST}.sv

VERILOG_DESIGN += ${XILINX_IP_SOURCES} ${RTL_SOURCES} ${SIM_SOURCES} ${IMPORT_SOURCES}

VERILOG_SOURCES = \
    ${VERILOG_DESIGN} \
    ${DUT_SOURCES}

include ${WORK_BASE}/rtlflo/cocotb_helper.mak
