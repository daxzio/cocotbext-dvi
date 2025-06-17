COV_ARGS += $(addprefix -P "${CONV_TOPLEVEL}., $(addsuffix ", $(CONV_GENERICS)))
COV_ARGS += -pdebug=1

vlog2vhdl:
	iverilog \
    	-g2012 \
    	-t vhdl \
		${COV_ARGS} \
    	${CONV_VERILOG_SOURCES} \
    	-o ${VHDL_OUTPUT}

vhdl2vlog:
# 	vhdl2vlog -t rgb2dvi ${VHDL_SOURCES}
	rm -rf unisim/v08
	mkdir -p unisim/v08
	ghdl -a --mb-comments -fexplicit -Whide -Wbinding --ieee=synopsys --no-vital-checks --std=08 -frelaxed \
		-v \
		--work=unisim \
		--workdir=./unisim/v08 \
			"./vhdl_src/unisim_VPKG.vhd" \
			"./vhdl_src/unisim_retarget_VCOMP.vhd" \
			"./vhdl_src/MMCME2_ADV.vhd" \
			"./vhdl_src/BUFIO.vhd" \
			"./vhdl_src/BUFR.vhd" \
			"./vhdl_src/PLLE2_ADV.vhd" \
			"./vhdl_src/OBUFDS.vhd"\
			"./vhdl_src/OSERDESE1.vhd"
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/DVI_Constants.vhd
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/SyncAsync.vhd
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/SyncAsyncReset.vhd
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/TMDS_Encoder.vhd
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/OutputSERDES.vhd
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/ClockGen.vhd
	ghdl -a --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/rgb2dvi.vhd
	ghdl synth --out=verilog -o=rgb2dvi.v --vendor-library=unisim --std=08 -fsynopsys -fexplicit -frelaxed rgb2dvi
# 
# 
# 	ghdl -a -v -P./unisim/v93 --std=93c -fsynopsys -fexplicit -frelaxed --ieee=synopsys /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/OutputSERDES.vhd
# 	ghdl -a -v -P/mnt/sda/projects/cocotbext-dvi/tests/xilinx-vivado.2024.2/unisim --std=08 -fsynopsys -fexplicit -frelaxed /mnt/sda/projects/cocotbext-dvi/tests/rtl/rgb2dvi/OutputSERDES.vhd
