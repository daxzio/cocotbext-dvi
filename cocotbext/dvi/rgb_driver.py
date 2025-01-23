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

from cocotb.triggers import RisingEdge
from cocotb import start_soon
from cocotb.utils import get_sim_time

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .rgbimage import RGBImage

# from .sigorvar import SignalOrVariable
from .sync_driver import syncDriver


class RGBDriver(CocoTBExtLogger):
    def __init__(
        self,
        clk,
        bus,
        image_file=None,
        frequency=60,
        height=None,
        width=None,
        logging_enabled=True,
    ):
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
        self.bus = bus
        self.log.info("RGB Driver")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023-2025 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")
        #         self.log.info(f"Generating Clock frequency: {self.clk_freq} MHz")
        self.clk = clk
        self.height = height
        self.width = width
        if isinstance(image_file, (list, tuple)):
            self.image_file = image_file
        else:
            self.image_file = [image_file]

        self.frequency = frequency
        self.offset_start = 20
        self.sync_edge = 0
        #         self.sync = syncDriver(None, frequency=self.frequency, offset_start=200000)
        self.sync = syncDriver(
            None, frequency=self.frequency, offset_start=self.offset_start
        )

        self.de = self.bus.de
        self.data = self.bus.data
        self.vsync = self.bus.vsync
        self.hsync = self.bus.hsync

        self.de.value = 0
        self.data.value = 0
        self.vsync.value = 0
        self.hsync.value = 0

        self.vsync_cnt = 0
        self.hsync_cnt = 0

        self.map = {
            0: 0,
            1: 1,
            2: 2,
        }

        self._restart()

    def _restart(self):
        start_soon(self._gen_rgb())
        start_soon(self._edge_sync())

    async def _gen_rgb(self):
        img_index = 0
        # Read first image to get dimensions, it is assumed that all subsequent images
        # will be of the same dimensions
        self.img = RGBImage(
            self.image_file[img_index], height=self.height, width=self.width
        )
        row_cnt = 0
        col_cnt = 0
        hsync_width = self.img.width + 250
        vsync_indent = 1
        vsync_start = vsync_indent * hsync_width
        vsync_end = vsync_start + (hsync_width * (self.img.height + 4))
        dimesion_delta = 2
        while True:
            await RisingEdge(self.clk)
            if self.sync.sync.value:
                break
        while True:
            await RisingEdge(self.clk)
            self.data.value = 0
            hsync_offset = vsync_indent + 1 + dimesion_delta
            if self.hsync_cnt < hsync_offset or self.hsync_cnt >= (
                hsync_offset + self.img.height
            ):
                col_cnt = 0
                self.de.value = False
            elif (self.vsync_cnt % hsync_width) < 8:
                self.de.value = False
            elif (self.vsync_cnt % hsync_width) >= (8 + self.img.width):
                self.de.value = False
            else:
                self.de.value = True
                x = int(self.img[row_cnt, col_cnt, self.map[0]])
                y = int(self.img[row_cnt, col_cnt, self.map[1]])
                z = int(self.img[row_cnt, col_cnt, self.map[2]])
                data = x + (y << 8) + (z << 16)
                self.data.value = data
                if col_cnt == self.img.width - 1:
                    col_cnt = 0
                    row_cnt = (row_cnt + 1) % self.img.height
                else:
                    col_cnt += 1

            if (self.vsync_cnt % hsync_width) < 4:
                self.hsync.value = False
                if 0 == (self.vsync_cnt % hsync_width):
                    self.hsync_cnt += 1
            else:
                self.hsync.value = True

            if self.vsync_cnt < vsync_start:
                self.vsync.value = False
            elif self.vsync_cnt > vsync_end - 1:
                self.vsync.value = False
            else:
                self.vsync.value = True

            if self.sync_edge:
                self.vsync_cnt = 0
                self.hsync_cnt = 0
                row_cnt = 0
                try:
                    self.img = RGBImage(
                        self.image_file[img_index], height=self.height, width=self.width
                    )
                    self.log.info(
                        f"Generating image {img_index} {self.img.width}x{self.img.height} @ {self.frequency} Hz"
                    )
                    img_index += 1
                except IndexError:
                    self.log.info(
                        f"Reusing image {img_index-1} {self.img.width}x{self.img.height} @ {self.frequency} Hz"
                    )
                    pass
                self.log.info(f"\t{self.img.image_file}")
            else:
                self.vsync_cnt = self.vsync_cnt + 1

    async def _edge_sync(self):
        sync_last = 0
        while True:
            await RisingEdge(self.clk)
            self.sync_edge = 0
            if 1 == self.sync.sync.value and 0 == sync_last:
                if self.vsync.value:
                    self.log.warning(
                        f"Last frames is not complete, frequency is too fast, {self.frequency} Hz"
                    )
                self.log.info(f"Sync edge detected, {get_sim_time('ns')}")
                self.sync_edge = 1
            sync_last = self.sync.sync.value

    async def await_start(self):
        while True:
            await RisingEdge(self.clk)
            if not 0 == self.vsync_cnt or not 0 == self.hsync_cnt:
                return

    async def await_image(self):
        while True:
            await RisingEdge(self.clk)
            if 0 == self.vsync_cnt and 0 == self.hsync_cnt:
                return
