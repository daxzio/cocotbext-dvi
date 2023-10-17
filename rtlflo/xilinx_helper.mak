XILINX_REV?=2021.2
XILINX_PART?=xc7a100tcsg324-1
CDSLIB?=./cds_${SIM}.lib
XILINX_LIB=${PROJ_HOME}/xilinx_lib

ifneq ($(XILINX_BASE),)
	UNISIMS = \
	    ${XILINX_BASE}/verilog/src/unisims/FDRE.v \
	    ${XILINX_BASE}/verilog/src/unisims/FDSE.v \
	    ${XILINX_BASE}/verilog/src/unisims/GND.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT1.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT2.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT3.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT4.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT5.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT6.v \
	    ${XILINX_BASE}/verilog/src/unisims/MUXF7.v \
	    ${XILINX_BASE}/verilog/src/unisims/MUXF8.v \
	    ${XILINX_BASE}/verilog/src/unisims/SRL16E.v \
	    ${XILINX_BASE}/verilog/src/unisims/SRLC32E.v \
	    ${XILINX_BASE}/verilog/src/unisims/OBUFDS.v \
	    ${XILINX_BASE}/verilog/src/unisims/BUFG.v \
	    ${XILINX_BASE}/verilog/src/unisims/IBUF.v \
	    ${XILINX_BASE}/verilog/src/unisims/MMCME2_ADV.v 
    
    ifeq ($(SIM), icarus)
        ifneq ($(XILINX_IP_SOURCES),)
			COMPILE_ARGS += -y${XILINX_BASE}/verilog/src/unisims
			COMPILE_ARGS += -s glbl
		endif
	else ifeq ($(SIM),xcelium)
		COMPILE_ARGS += -top glbl
		VERILOG_SOURCES += \
			${XILINX_BASE}/verilog/src/glbl.v
	    VERILOG_SOURCES += ${UNISIMS} 
	else ifeq ($(SIM),ius)
# 		COMPILE_ARGS += -y unisims_ver
		COMPILE_ARGS += -cdslib ${CDSLIB}
    else ifeq ($(SIM),verilator)
	    COMPILE_ARGS += --top-module glbl
		VERILOG_SOURCES += \
			${XILINX_BASE}/verilog/src/glbl.v
	    VERILOG_SOURCES += ${UNISIMS} 
    endif
        
endif

default: sim

${CDSLIB}:
	echo "DEFINE unisims_ver ${XILINX_LIB}/${SIM}/unisims_ver" >> ${CDSLIB}

${XILINX_LIB}/ius/unisims_ver:
	mkdir -p ${XILINX_LIB}/ius/unisims_ver
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver -f ${RTLFLOW_PATH}/xilinx/unisims_ver/.cxl.verilog.unisim.unisims_ver.lin64.cmf
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/MMCME2_ADV.v
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver /opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/secureip/iserdese2/iserdese2_002.vp
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -SV -WORK unisims_ver -f ${RTLFLOW_PATH}/xilinx/unisims_ver/.cxl.systemverilog.unisim.unisims_ver.lin64.cmf

${XILINX_LIB}/xcelium/unisims_ver:
	mkdir -p ${XILINX_LIB}/xcelium/unisims_ver
	xmvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver -f ${RTLFLOW_PATH}/xilinx/unisims_ver/.cxl.verilog.unisim.unisims_ver.lin64.cmf
	xmvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/MMCME2_ADV.v
	xmvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -SV -WORK unisims_ver -f ${RTLFLOW_PATH}/xilinx/unisims_ver/.cxl.systemverilog.unisim.unisims_ver.lin64.cmf

ius_lib: | ${CDSLIB} ${XILINX_LIB}/ius/unisims_ver

xcelium_lib: | ${CDSLIB} ${XILINX_LIB}/xcelium/unisims_ver

# test:
# 	vivado -mode batch -tcl \
# 	"compile_simlib \
# 		-dir {/home/dkeeshan/projects/temp/xilinx_lib} \
# 		-simulator xcelium \
# 		-simulator_exec_path {/opt/tools/redhat8_x86/cadence/XCELIUM2209/004/tools/bin/64bit} \
# 		-language verilog \
# 		-library unisim \
# 		-verbose \
# 		-family all"

xilinx_library:
	mkdir -p ${XILINX_LIB}
ifeq ($(SIM),ius)
	${MAKE} ius_lib
else ifeq ($(SIM),xcelium)
	${MAKE} xcelium_lib
endif


git_xilinx:
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.ip_user_files/ip/*/*_sim_netlist.v -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.srcs/sources_1/ip/*.xcix
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.xpr
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.ip_user_files/ip/*/*_sim_netlist.v -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.srcs/sources_1/ip/*.xcix
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.xpr
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.ip_user_files/ip/*/*_sim_netlist.v -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.srcs/sources_1/ip/*.xcix
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.xpr
