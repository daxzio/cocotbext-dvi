"""

Copyright (c) 2023-2025 Daxzio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import logging

from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb import start_soon
from cocotb.utils import get_sim_time

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .tmds import TMDS
from .rgbimage import RGBImage
from .rgb_sink import RGBSink
from .rgb_bus import DummyRGBBus


class DVISink(CocoTBExtLogger):
    def __init__(
        self,
        dut,
        bus,
        rgb_bus=None,
        image_file=None,
        expected_frequency=None,
        height=-1,
        width=-1,
    ):
        CocoTBExtLogger.__init__(self, type(self).__name__)

        self.bus = bus
        self.rgb_bus = rgb_bus
        self.image_file = image_file
        self.img = RGBImage(self.image_file)

        self.log.info("DVI Sink")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023-2025 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")
        self.log.setLevel(logging.INFO)

        self.clk = self.bus.clk_p
        self.data = self.bus.data_p

        if self.rgb_bus is None:
            self.rgb_bus = DummyRGBBus()

        self.rgb_out = RGBSink(
            self.clk,
            self.rgb_bus,
            image_file=self.image_file,
            expected_frequency=expected_frequency,
            height=height,
            width=width,
        )

        self.start = False
        self.time_delta = 0

        self.tmds = [TMDS(), TMDS(), TMDS()]
        self.tmdsin = [0, 0, 0]

        self._restart()

    @property
    def verification(self):
        return self.rgb_out.verification

    @verification.setter
    def verification(self, value):
        self.rgb_out.verification = value

    @property
    def verify_start(self):
        return self.rgb_out.verify_start

    @verify_start.setter
    def verify_start(self, value):
        self.rgb_out.verify_start = value

    async def wait_bit(self, amount=1.0):
        await Timer(int(amount * self.time_delta) / 5, units="fs")

    def _restart(self):
        start_soon(self._detect_clk())
        start_soon(self._detect_data())
        start_soon(self._parse_data())

    async def _detect_clk(self):
        await RisingEdge(self.clk)
        t0 = get_sim_time("fs")
        await FallingEdge(self.clk)
        t1 = get_sim_time("fs")
        self.time_delta = t1 - t0

        self.start = True
        self.clk_freq = 1000000000 / (2 * self.time_delta)
        self.log.info(f"Detected Clock frequency: {self.clk_freq} MHz")
        while True:
            await RisingEdge(self.clk)
            t0 = get_sim_time("fs")
            await FallingEdge(self.clk)
            t1 = get_sim_time("fs")
            new_time_delta = t1 - t0
            new_freq = 1000000000 / (2 * new_time_delta)
            if not new_freq == self.clk_freq:
                raise Exception(
                    f"Change in clock frequency detected {new_freq} {self.clk_freq}"
                )

    async def _detect_data(self):
        self.rgb_out.hsync.value = False
        self.rgb_out.vsync.value = False
        self.rgb_out.de.value = False
        while True:
            await FallingEdge(self.clk)
            if self.start:
                await self.wait_bit(0.5)
                self.tmdsin = [0, 0, 0]
                for i in range(10):
                    for j, _ in enumerate(self.tmdsin):
                        self.tmdsin[j] |= int((self.data.value >> j) & 0x1) << i
                    if i < 9:
                        await self.wait_bit()

                data = 0
                for i in range(len(self.tmds)):
                    self.tmds[i].decode(self.tmdsin[i])
                    if self.tmds[i].de:
                        data += self.tmds[i].dataout << (8 * i)
                self.rgb_out.data.value = data
                self.rgb_out.de.value = self.tmds[0].de
                if not self.tmds[0].de:
                    self.rgb_out.hsync.value = self.tmds[0].hsync
                    self.rgb_out.vsync.value = self.tmds[0].vsync

    async def _parse_data(self):
        self.frame_complete = False
        self.vsync_last = False
        while True:
            await FallingEdge(self.clk)
            self.frame_complete = not (self.rgb_out.vsync) and self.vsync_last
            self.vsync_last = self.rgb_out.vsync

    async def frame_finished(self):
        await self.rgb_out.frame_finished()


#     def report_frame(self):
#         self.rgb_out.report_frame()
