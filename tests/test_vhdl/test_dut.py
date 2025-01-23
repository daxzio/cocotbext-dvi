from cocotb import start_soon
from cocotb import test
from cocotb.triggers import Timer

from cocotbext.dvi import DVIDriver
from cocotbext.dvi import DVISink
from cocotbext.dvi import RGBDriver
from cocotbext.dvi import RGBSink
from cocotbext.dvi import RGBBus
from cocotbext.dvi import DVIBus

from interfaces.clkrst import Clk
from interfaces.detect_clk import detect_clk


class testbench:
    def __init__(self, dut):
        period = 40
        self.clk = Clk(dut, period, units="ns", clkname="PixelClk")

        start_soon(detect_clk(self.clk.clk, "pixelclk", 25))
        start_soon(self.timeout())
    
    async def timeout(self, time=5000000, units='ns'):
        await Timer(time, units)
        raise Exception(f'Timeout occurred! {time} {units}')

@test()
async def test_rgb(dut):
    tb = testbench(dut)

    signals_in = {
        "vsync": "vid_in_vsync",
        "hsync": "vid_in_hsync",
        "de": "vid_in_de",
        "data": "vid_in_data",
    }
    rgb_in_bus = RGBBus(dut, signals=signals_in)

    rgb_in = RGBDriver(
        tb.clk.clk,
        rgb_in_bus,
        image_file="./images/320x240.bmp",
        frequency=1600,
        height=20,
    )

    signals_out = {
        "vsync": "vid_out_vsync",
        "hsync": "vid_out_hsync",
        "de": "vid_out_de",
        "data": "vid_out_data",
    }
    rgb_out_bus = RGBBus(dut, signals=signals_out)
    rgb_out = RGBSink(
        tb.clk.clk,
        rgb_out_bus,
        image_file="./images/320x240.bmp",
        expected_frequency=1600,
        height=20,
    )

    await rgb_out.frame_finished()
    await rgb_out.frame_finished()

    await tb.clk.end_test()


@test()
async def test_dvi(dut):
    tb = testbench(dut)

    signals_in = {
        "clk_p": "tmds_in_clk_p",
        "clk_n": "tmds_in_clk_n",
        "data_p": "tmds_in_data_p",
        "data_n": "tmds_in_data_n",
    }
    dvi_in_bus = DVIBus(dut, signals=signals_in)
    dvi_in = DVIDriver(
        dut,
        dvi_in_bus,
        image_file="./images/320x240.bmp",
        clk_freq=25.0,
        frequency=1600,
        height=20,
    )

    signals_out = {
        "clk_p": "tmds_out_clk_p",
        "clk_n": "tmds_out_clk_n",
        "data_p": "tmds_out_data_p",
        "data_n": "tmds_out_data_n",
    }
    dvi_out_bus = DVIBus(dut, signals=signals_out)
    dvi_out = DVISink(
        dut,
        dvi_out_bus,
        image_file="./images/320x240.bmp",
        expected_frequency=1600,
        height=20,
    )

    await dvi_out.frame_finished()
    await dvi_out.frame_finished()

    await tb.clk.end_test()


@test()
async def test_dvi_debug(dut):
    tb = testbench(dut)

    signals_in = {
        "clk_p": "tmds_in_clk_p",
        "clk_n": "tmds_in_clk_n",
        "data_p": "tmds_in_data_p",
        "data_n": "tmds_in_data_n",
    }
    dvi_in_bus = DVIBus(dut, signals=signals_in)
    signals_in = {
        "vsync": "vid_in_vsync",
        "hsync": "vid_in_hsync",
        "de": "vid_in_de",
        "data": "vid_in_data",
    }
    rgb_in_bus = RGBBus(dut, signals=signals_in)
    dvi_in = DVIDriver(
        dut,
        dvi_in_bus,
        rgb_bus=rgb_in_bus,
        image_file="./images/320x240.bmp",
        clk_freq=25.0,
        frequency=1600,
        height=20,
    )

    signals_out = {
        "clk_p": "tmds_out_clk_p",
        "clk_n": "tmds_out_clk_n",
        "data_p": "tmds_out_data_p",
        "data_n": "tmds_out_data_n",
    }
    dvi_out_bus = DVIBus(dut, signals=signals_out)
    signals_out = {
        "vsync": "vid_out_vsync",
        "hsync": "vid_out_hsync",
        "de": "vid_out_de",
        "data": "vid_out_data",
    }
    rgb_out_bus = RGBBus(dut, signals=signals_out)
    dvi_out = DVISink(
        dut,
        dvi_out_bus,
        rgb_bus=rgb_out_bus,
        image_file="./images/320x240.bmp",
        expected_frequency=1600,
        height=20,
    )

    await dvi_out.frame_finished()
    await dvi_out.frame_finished()

    await tb.clk.end_test()
