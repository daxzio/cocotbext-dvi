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


from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb import start_soon
from cocotb.utils import get_sim_time

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .rgbimage import RGBImage
from .sigorvar import SignalOrVariable


class RGBHsync:
    def __init__(self, vsync=False, expected_length=None):
        self.vsync = vsync
        self.start = None
        self.end = None
        self.expected_length = expected_length
        self.start_time()

    def start_time(self):
        self.start = get_sim_time("step")

    def end_time(self, vsync, test=True):
        self.end = get_sim_time("step")
        if not self.expected_length is None and test:
            if not self.expected_length == self.length:
                raise Exception(
                    f"Hsync length changes {self.expected_length} != {self.length}"
                )

    @property
    def length(self):
        return self.end - self.start


class RGBVsync:
    def __init__(self, expected_length=None):
        self.start = None
        self.end = None
        self.expected_length = expected_length
        self.start_time()

    def start_time(self):
        self.start = get_sim_time("step")

    def end_time(self):
        self.end = get_sim_time("step")
        if not self.expected_length is None:
            if not self.expected_length == self.length:
                raise Exception

    @property
    def length(self):
        return self.end - self.start


class RGBFrame(CocoTBExtLogger):
    num = -1

    def __init__(self, image_file=None, verify=True):
        RGBFrame.num += 1
        logging_enabled = False
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)
        self.image_file = image_file
        self.img = RGBImage(self.image_file)
        self.x = 0
        self.y = 0
        self.col_cnt = 0
        self.hsync = []
        self.vsync = RGBVsync()
        self.data = [[], [], []]
        self.start = None
        self.end = None
        self.verify = verify
        self.start_time()
        self.clk_time = 80 * 1000

    def start_time(self):
        self.start = get_sim_time("step")

    def end_frame(self):
        self.vsync.end_time()
        self.end = get_sim_time("step")

    def setdata(self, key, value):
        if self.verify:
            if self.image_file is None:
                raise Exception("No image was defined to verify against!")
            expected_value = self.img[self.y][self.x][key]
            if not value == expected_value:
                raise Exception(
                    f"Expected value 0x{expected_value:02x} does not match Detected 0x{value:02x}"
                )
            if key == 2:
                if self.x < self.img.width - 1:
                    self.x += 1
                else:
                    self.x = 0
                    self.y += 1
                    self.log.debug(
                        f"Frame {self.num} Row {self.y}/{self.img.height} completed"
                    )

        self.data[key].append(value)

    def report_frame(self):
        if self.verify:
            if not len(self.hsync) == self.img.width + 10:
                raise Exception(
                    f"Incorrect number of hsync detected {len(self.hsync)} expected {self.img.width+10}"
                )
            expected_vsync_length = (self.img.width + 10) * self.img.width * self.clk_time
            if not self.vsync.length == expected_vsync_length:
                raise Exception(
                    f"Expected vsync length {expected_vsync_length} does not match Detected {self.vsync.length}"
                )
        self.log.warning(f"Frame {self.num} completed verify {self.verify}")


class RGBSink(CocoTBExtLogger):
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

        self.image_file = image_file
        self.img = RGBImage(self.image_file)

        self.log.info("RGB Sink")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")

        self.clk = clk
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

        self.first_vsync = False
        self.verify = True
        self.frames = []
        self.row_cnt = 0
        self.col_cnt = 0
        self.hsync_last = False
        self.vsync_last = False
        self.frame_complete = False

        start_soon(self._parse_data())

    async def _parse_data(self):
        hsync_expected_length = None
        while True:
            await FallingEdge(self.clk)
            self.frame_complete = False
            if not self.vsync_last and self.vsync.value:
                self.log.debug(f"vsync start detected")
                if self.first_vsync:
                    self.f.end_frame()
                    self.f.report_frame()
                    self.frame_complete = True
                    self.frames.append(self.f)
                self.first_vsync = True
                self.f = RGBFrame(self.image_file, self.verify)
                self.row_cnt = 0
            if self.vsync_last and not self.vsync.value:
                self.log.debug(f"vsync end detected")
                if not self.img.height == self.row_cnt and self.verify:
                    raise Exception(
                        f"Incorrect number of rows per frame {self.row_cnt}"
                    )

            if not self.hsync_last and self.hsync.value:
                self.log.debug(f"hsync start detected")
                h = RGBHsync(self.vsync.value)
                h.expected_length = hsync_expected_length
                self.col_cnt = 0
            if self.hsync_last and not self.hsync.value:
                self.log.debug(f"hsync end detected")

                if (
                    not 0 == self.col_cnt
                    and not self.img.width == self.col_cnt
                    and self.verify
                ):
                    raise Exception(
                        f"Incorrect number of data valids per row {self.col_cnt}"
                    )
                if not 0 == self.col_cnt:
                    self.row_cnt += 1
                # h.end_time(self.vsync.value, self.first_vsync)
                h.end_time(self.vsync.value, self.verify)
                hsync_expected_length = h.length
                if self.first_vsync:
                    self.f.hsync.append(h)
                del h
            if self.first_vsync:
                if self.de.value:
                    self.col_cnt += 1
                    for i in range(len(self.data)):
                        self.f.setdata(i, self.data[i].value)

            self.hsync_last = self.hsync.value
            self.vsync_last = self.vsync.value

    async def frame_finished(self):
        while True:
            await RisingEdge(self.clk)
            if self.frame_complete:
                self.log.debug(f"Frame finished detected")
                break
