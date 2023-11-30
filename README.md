# DVI and RGB interface modules for Cocotb

GitHub repository: https://github.com/daxzio/cocotbext-dvi

## Introduction

DVI and RGB simulation models for [cocotb](https://github.com/cocotb/cocotb).

## Installation

Installation from git (latest development version, potentially unstable):

    $ pip install https://github.com/daxzio/cocotbext-dvi/archive/master.zip

Installation for active development:

    $ git clone https://github.com/daxzio/cocotbext-dvi
    $ pip install -e cocotbext-dvi

## Documentation and usage examples

See the `tests` directory and [verilog-i2c](https://github.com/daxzio/verilog-i2c) for complete testbenches using these modules.

        image_file = "/home/dkeeshan/projects/cocotbext-dvi/tests/images/160x120.bmp"
        self.dvi_in = DVIDriver(dut, image_file)
    def __init__(self, dut, image_file=None, dvi_prefix="tmds_in", clk_freq=25.0):


        image_file = "/home/dkeeshan/projects/cocotbext-dvi/tests/images/160x120.bmp"
        self.dvi_out = DVISink(dut, image_file)
    def __init__(self, dut, image_file=None, dvi_prefix="tmds_out"):

    def __init__(self, clk, image_file=None, vsync=None, hsync=None, data_valid=None, data0=None, data1=None, data2=None, logging_enabled=True):
