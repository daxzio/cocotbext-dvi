XILINX_REV?=2021.2
XILINX_PART?=xc7a100tcsg324-1
CDSLIB?=./cds_${SIM}.lib
COMPILE_LIBS?=../../libs
RTLFLO_PATH?=../../rtlflo

ifneq ($(XILINX_VIVADO),)
XILINX_BASE?=${XILINX_VIVADO}/data
endif

ifneq (${XILINX_BASE},)
	UNISIMS_VER_CNT=`grep -s unisims_ver ${CDSLIB} | wc -l`
	UNISIMS_VHDL_CNT=`grep -s unisim ${CDSLIB} | wc -l`
	
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
		COMPILE_ARGS += -top glbl
		VERILOG_SOURCES += \
			${XILINX_BASE}/verilog/src/glbl.v
		COMPILE_ARGS += -cdslib ${CDSLIB}
    else ifeq ($(SIM),verilator)
	    COMPILE_ARGS += --top-module glbl
		VERILOG_SOURCES += \
			${XILINX_BASE}/verilog/src/glbl.v
	    VERILOG_SOURCES += ${UNISIMS} 
    endif
        
endif

default: sim

xilinx_cdslib:
	@if [ "${UNISIMS_VHDL_CNT}" -eq "0" ]; then \
		mkdir -p ${COMPILE_LIBS}/${SIM}/xilinx/unisim ; \
		mkdir -p ${COMPILE_LIBS}/${SIM}/xilinx/secureip ; \
		echo "DEFINE unisim ${COMPILE_LIBS}/${SIM}/xilinx/unisim" >> ${CDSLIB} ; \
		echo "DEFINE secureip ${COMPILE_LIBS}/${SIM}/xilinx/secureip" >> ${CDSLIB} ; \
	fi
	@if [ "${UNISIMS_VER_CNT}" -eq "0" ]; then \
		mkdir -p ${COMPILE_LIBS}/${SIM}/xilinx/unisims_ver ; \
		echo "DEFINE unisims_ver ${COMPILE_LIBS}/${SIM}/xilinx/unisims_ver" >> ${CDSLIB} ; \
	fi
	

${COMPILE_LIBS}/ius/xilinx/unisim: ${CDSLIB} xilinx_cdslib
	ncvhdl -MESSAGES -NOLOG -64bit -v93 -CDSLIB ${CDSLIB} -WORK unisim \
		${XILINX_BASE}/vhdl/src/unisims/unisim_VPKG.vhd \
		${XILINX_BASE}/vhdl/src/unisims/unisim_VCOMP.vhd \
		${XILINX_BASE}/vhdl/src/unisims/primitive/*.vhd 
	ncvhdl -MESSAGES -NOLOG -64bit -v93 -CDSLIB ${CDSLIB} -WORK secureip \
		${XILINX_BASE}/vhdl/src/unisims/secureip/*.vhd 

${COMPILE_LIBS}/ius/xilinx/unisims_ver: ${CDSLIB} xilinx_cdslib
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/*.v
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -SV -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/*.sv
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/secureip/*/*.vp

${COMPILE_LIBS}/xcelium/unisims_ver: ${CDSLIB} xilinx_cdslib
# 	mkdir -p ${COMPILE_LIBS}/${SIM}/xilinx/unisims_ver
# 	@if [ "${UNISIMS_VER_CNT}" -eq "0" ]; then \
# 		echo "DEFINE unisims_ver ${COMPILE_LIBS}/${SIM}/xilinx/unisims_ver" >> ${CDSLIB} ; \
# 	fi
	xmvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/*.v
	xmvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -SV -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/*.sv

xilinx_ius_lib: | ${COMPILE_LIBS}/ius/xilinx/unisims_ver ${COMPILE_LIBS}/ius/xilinx/unisim

xilinx_xcelium_lib: | ${COMPILE_LIBS}/ius/xilinx/unisims_ver ${COMPILE_LIBS}/xcelium/unisim

#ncvhdl -MESSAGES -NOLOG -64bit -v93 -CDSLIB ./cds_ius.lib -WORK unisim  /opt/tools/redhat8_x86/xilinx/Vivado/2021.2/data/vhdl/src/unisims/primitive/MMCME2_ADV.vhd 

# test:
# 	vivado -mode batch -tcl \
# 	"compile_simlib \
# 		-dir {/home/dkeeshan/projects/temp/COMPILE_LIBS} \
# 		-simulator xcelium \
# 		-simulator_exec_path {/opt/tools/redhat8_x86/cadence/XCELIUM2209/004/tools/bin/64bit} \
# 		-language verilog \
# 		-library unisim \
# 		-verbose \
# 		-family all"

xilinx_library:
	mkdir -p ${COMPILE_LIBS}
ifeq ($(SIM),ius)
	${MAKE} xilinx_ius_lib
else ifeq ($(SIM),xcelium)
	${MAKE} xilinx_xcelium_lib
endif

xilinx_library_clean:
	@rm -rf ${COMPILE_LIBS}/${SIM}/xilinx
	@sed -in '/unisim/d' ${CDSLIB} || true
	@sed -in '/secureip/d' ${CDSLIB} || true

cdslib:: xilinx_cdslib

all_libs:: xilinx_library

all_libs_clean:: xilinx_library_clean

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
