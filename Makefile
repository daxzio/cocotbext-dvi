SIM?=icarus
PASSPHRASE?=12345678

default: vhdl verilog

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

black: format

checks: format lint mypy

dist:
	rm -rf MANIFEST 
	rm -rf CHANGELOG.txt
	python setup.py sdist

GIT_TAG?=0.1.0
VERSION_FILE?=`find . -name version.py`
release:
	echo "Release v${GIT_TAG}"
# 	@grep -Po '\d\.\d\.\d' cocotbext/jtag/version.py
	git tag v${GIT_TAG} || { echo "make release GIT_TAG=0.1.0"; git tag ; exit 1; }
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

gpg_tar:
	rm -rf tests/vhdl_src.tgz.gpg
	cd repos ; tar -cvf ../vhdl_src.tgz vhdl_src/
	@gpg --symmetric --cipher-algo aes256 --batch --passphrase ${PASSPHRASE} vhdl_src.tgz
	mv vhdl_src.tgz.gpg tests/.
	rm -rf vhdl_src.tgz*

gpg_untar:
	@cd tests ; rm -rf vhdl_src vhdl_src.tgz ; gpg --output vhdl_src.tgz --decrypt --batch  --passphrase ${PASSPHRASE} vhdl_src.tgz.gpg
	@cd tests ; tar -xf vhdl_src.tgz

compile_unisim:
	rm -rf ./tests/xilinx-vivado
	mkdir -p ./tests/xilinx-vivado/unisim/v93
	mkdir -p ./tests/xilinx-vivado/unisim/v08
	@ghdl -a --mb-comments -fexplicit -Whide -Wbinding --ieee=synopsys --no-vital-checks --std=93c -frelaxed \
		-P./tests/xilinx-vivado \
		--work=unisim \
		--workdir=./tests/xilinx-vivado/unisim/v93 \
			./tests/vhdl_src/unisim_VPKG.vhd \
			./tests/vhdl_src/unisim_retarget_VCOMP.vhd \
			./tests/vhdl_src/primitives/*.vhd
# 	@ghdl -a --mb-comments -fexplicit -Whide -Wbinding --ieee=synopsys --no-vital-checks --std=08 -frelaxed \
# 		-P./tests/xilinx-vivado \
# 		--work=unisim \
# 		--workdir=./tests/xilinx-vivado/unisim/v93 \
# 			./tests/vhdl_src/unisim_VPKG.vhd \
# 			./tests/vhdl_src/unisim_retarget_VCOMP.vhd \
# 			./tests/vhdl_src/primitives/*.vhd
