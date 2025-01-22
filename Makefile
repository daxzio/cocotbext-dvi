SIM?=icarus

default: verilog vhdl

vhdl:
	cd tests/test_vhdl ; make clean sim SIM=ghdl WAVES=0 && ../../rtlflo/combine_results.py
	cd tests/test_rgb2dvi ; make clean sim SIM=ghdl WAVES=0 && ../../rtlflo/combine_results.py

verilog:
	cd tests/test_verilog ; make clean sim WAVES=0 && ../../rtlflo/combine_results.py


lint:
	pyflakes cocotbext
	ruff check cocotbext

mypy:
	mypy cocotbext

format:
	black cocotbext

checks: format lint mypy

dist:
	rm -rf MANIFEST 
	rm -rf CHANGELOG.txt
	python setup.py sdist

GIT_TAG?=0.0.1
VERSION_FILE?=`find . -name version.py`
release:
	echo "Release v${GIT_TAG}"
# 	@grep -Po '\d\.\d\.\d' cocotbext/jtag/version.py
	git tag v${GIT_TAG} || { echo "make release GIT_TAG=0.0.5"; git tag ; exit 1; }
	echo "__version__ = \"${GIT_TAG}\"" > ${VERSION_FILE}
	git add ${VERSION_FILE}
	git commit --allow-empty -m "Update to version ${GIT_TAG}"
	git tag -f v${GIT_TAG}
	git push && git push --tags

git_align:
	mkdir -p repos tests/rtl
	cd repos ; git clone git@github.com:daxzio/rtlflo.git 2> /dev/null || (cd rtlflo ; git pull)
	rsync -artu --exclude .git repos/rtlflo/ rtlflo
	rsync -artu --exclude .git rtlflo/ repos/rtlflo
	cd repos ; git clone git@github.com:daxzio/vivado-library.git 2> /dev/null || (cd vivado-library ; git checkout develop ;git pull)
	rsync -artu --exclude .git repos/vivado-library/ip/dvi2rgb/src/ tests/rtl/dvi2rgb
	rsync -artu --exclude .git tests/rtl/dvi2rgb/ repos/vivado-library/ip/dvi2rgb/src
	rsync -artu --exclude .git repos/vivado-library/ip/rgb2dvi/src/ tests/rtl/rgb2dvi
	rsync -artu --exclude .git tests/rtl/rgb2dvi/ repos/vivado-library/ip/rgb2dvi/src

compile_unisim:
	rm -rf /mnt/sda/projects/cocotbext-dvi/tests/xilinx-vivado.2024.2
	mkdir -p /mnt/sda/projects/cocotbext-dvi/tests/xilinx-vivado.2024.2/unisim/v93
	ghdl -a --mb-comments -fexplicit -Whide -Wbinding --ieee=synopsys --no-vital-checks --std=93c -frelaxed \
		-P/mnt/sda/projects/cocotbext-dvi/tests/xilinx-vivado.2024.2 \
		-v \
		--work=unisim \
		--workdir=/mnt/sda/projects/cocotbext-dvi/tests/xilinx-vivado.2024.2/unisim/v93 \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/unisim_VPKG.vhd" \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/unisim_retarget_VCOMP.vhd" \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/primitive/MMCME2_ADV.vhd" \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/primitive/BUFIO.vhd" \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/primitive/BUFR.vhd" \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/primitive/PLLE2_ADV.vhd" \
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/primitive/OBUFDS.vhd"\
			"/mnt/sda/xilinx/Vivado/2024.2/data/vhdl/src/unisims/primitive/OSERDESE1.vhd"
