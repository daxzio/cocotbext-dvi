"""

Copyright (c) 2023 Daxzio

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

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .rgbimage import RGBImage
from .sigorvar import SignalOrVariable


class RGBDriver(CocoTBExtLogger):
    def __init__(
        self,
        clk,
        image_file=None,
        vsync=None,
        hsync=None,
        de=None,
        data0=None,
        data1=None,
        data2=None,
        logging_enabled=True,
    ):
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
        self.log.info("RGB Driver")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")
        self.clk = clk

        self.image_file = image_file
        self.img = RGBImage(self.image_file)

        self.vsync = SignalOrVariable(vsync)
        self.hsync = SignalOrVariable(hsync)
        self.de = SignalOrVariable(de)
        self.data = [
            SignalOrVariable(data0),
            SignalOrVariable(data1),
            SignalOrVariable(data2),
        ]

        self.vsync.setimmediatevalue(False)
        self.hsync.setimmediatevalue(False)
        self.de.setimmediatevalue(False)
        self.data[0].setimmediatevalue(False)
        self.data[1].setimmediatevalue(False)
        self.data[2].setimmediatevalue(False)

        self.vsync_cnt = 0
        self.hsync_cnt = 0

        self._restart()

    def _restart(self):
        start_soon(self._detect_clk())

    async def _detect_clk(self):
        row_cnt = 0
        col_cnt = 0
        while True:
            await RisingEdge(self.clk)
            self.data[0].value = 0
            self.data[1].value = 0
            self.data[2].value = 0
            #             hsync_offset = 36
            #             hsync_offset = 20
            hsync_offset = int((self.img.width - self.img.height) / 2)
            if self.hsync_cnt < hsync_offset or self.hsync_cnt >= (
                hsync_offset + self.img.height
            ):
                col_cnt = 0
                self.de.value = False
            elif (self.vsync_cnt % (2 * self.img.width)) < self.img.height:
                self.de.value = False
            elif (self.vsync_cnt % (2 * self.img.width)) >= (
                self.img.height + self.img.width
            ):
                self.de.value = False
            else:
                self.de.value = True
                self.data[0].value = int(self.img[row_cnt, col_cnt, 0])
                self.data[1].value = int(self.img[row_cnt, col_cnt, 1])
                self.data[2].value = int(self.img[row_cnt, col_cnt, 2])
                if col_cnt == self.img.width - 1:
                    col_cnt = 0
                    row_cnt = (row_cnt + 1) % self.img.height
                else:
                    col_cnt += 1

            if (self.vsync_cnt % (2 * self.img.width)) < (self.img.width / 5):
                self.hsync.value = False
                if 0 == (self.vsync_cnt % (2 * self.img.width)):
                    self.hsync_cnt += 1
            else:
                self.hsync.value = True

            if self.vsync_cnt < (int(self.img.height / 10) * self.img.width):
                self.vsync.value = False
            else:
                self.vsync.value = True

            if self.vsync_cnt == ((2 * self.img.width) * (self.img.width + 10)) - 1:
                self.vsync_cnt = 0
                self.hsync_cnt = 0
                row_cnt = 0
            else:
                self.vsync_cnt = self.vsync_cnt + 1
