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

from cocotb.triggers import RisingEdge, FallingEdge
from cocotb import start_soon
from cocotb.utils import get_sim_time

from .version import __version__
from .cocotbext_logger import CocoTBExtLogger
from .rgbimage import RGBImage


class RGBHsync:
    def __init__(self, vsync=False, expected_length=None):
        self.vsync = vsync
        self.start = None
        self.end = None
        self.expected_length = expected_length
        self.start_time()

    def start_time(self):
        self.start = get_sim_time("fs")

    def end_time(self, vsync, test=True):
        self.end = get_sim_time("fs")
        if self.expected_length is not None and test:
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
        self.start = get_sim_time("fs")

    def end_time(self):
        self.end = get_sim_time("fs")
        if self.expected_length is not None:
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
        self.data = []
        self.start = None
        self.end = None
        self.verification = verify
        self.start_time()
        self.clk_time = 80 * 1000

    def start_time(self):
        self.start = get_sim_time("fs")

    def end_frame(self):
        #         self.vsync.end_time()
        self.end = get_sim_time("fs")

    def setdata(self, value):
        if self.verification:
            if self.image_file is None:
                raise Exception("No image was defined to verify against!")
            for key in range(3):
                expected_value = self.img[self.y][self.x][key]
                test_value = (value >> (8 * key)) & 0xFF
                if not test_value == expected_value:
                    raise Exception(
                        f"Expected value 0x{expected_value:02x} does not match Detected 0x{test_value:02x} - [{self.y}][{self.x}][{key}]"
                    )
            if self.x < self.img.width - 1:
                self.x += 1
            else:
                self.x = 0
                self.y += 1
                self.log.debug(
                    f"Frame {self.num} Row {self.y}/{self.img.height} completed"
                )

        self.data.append(value)

    def report_frame(self):
        #         max_dimension = max(self.img.width, self.img.height)
        #         hsync_width = self.img.width
        #         if self.verification:
        #             if not len(self.hsync) == (self.img.width):
        #                 raise Exception(
        #                     f"Incorrect number of hsync detected {len(self.hsync)} expected {self.img.width+10}"
        #                 )
        #             expected_vsync_length = (
        #                 hsync_width * max_dimension * self.clk_time
        #             )
        #             if not self.vsync.length == expected_vsync_length:
        #                 raise Exception(
        #                     f"Expected vsync length {expected_vsync_length} does not match Detected {self.vsync.length}"
        #                     f"\n{int(expected_vsync_length/self.clk_time)} {int(self.vsync.length/self.clk_time)}"
        #                 )
        self.log.info(f"Frame {self.num} completed verify {self.verification}")


class RGBSink(CocoTBExtLogger):
    def __init__(
        self,
        clk,
        bus,
        image_file=None,
        expected_frequency=None,
        height=-1,
        width=-1,
        logging_enabled=True,
        clk_freq=25.0,
    ):
        CocoTBExtLogger.__init__(self, type(self).__name__, logging_enabled)

        self.image_file = image_file
        self.img = RGBImage(self.image_file)
        self.expected_frequency = expected_frequency
        if -1 == height:
            self.height = self.img.height
        else:
            self.height = height
        if -1 == width:
            self.width = self.img.width
        else:
            self.width = width

        self.log.info("RGB Sink")
        self.log.info(f"cocotbext-dvi version {__version__}")
        self.log.info("Copyright (c) 2023-2025 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-dvi")
        self.log.setLevel(logging.INFO)

        self.clk = clk
        self.bus = bus

        self.de = self.bus.de
        self.data = self.bus.data
        self.vsync = self.bus.vsync
        self.hsync = self.bus.hsync

        self.de.value = 0
        self.data.value = 0
        self.vsync.value = 0
        self.hsync.value = 0

        self.first_vsync = False
        self.verification = True
        self.verification_start = 0
        self.frames = []
        self.row_cnt = 0
        self.col_cnt = 0
        self.hsync_last = False
        self.vsync_last = False
        self.frame_complete = False
        #         self.clk_time = 80 * 1000
        self.clk_time = int(2000000 / clk_freq)

        start_soon(self._parse_data())
        start_soon(self._edge_sync())

    async def _parse_data(self):
        hsync_expected_length = None
        while True:
            await FallingEdge(self.clk)
            self.frame_complete = False
            if not self.vsync_last and self.vsync.value:
                self.log.debug("vsync start detected")
                if self.first_vsync:
                    self.f.end_frame()
                    self.f.report_frame()
                    self.frame_complete = True
                    self.frames.append(self.f)
                self.first_vsync = True
                if self.verification_start > len(self.frames):
                    self.verification = False
                else:
                    self.verification = self.verification
                self.f = RGBFrame(self.image_file, self.verification)
                self.row_cnt = 0
            if self.vsync_last and not self.vsync.value:
                self.log.debug("vsync end detected")
                self.f.vsync.end_time()
                if not self.height == self.row_cnt and self.verification:
                    raise Exception(
                        f"Incorrect number of rows per frame {self.row_cnt} - {self.height}"
                    )

            if not self.hsync_last and self.hsync.value and self.vsync_last:
                self.log.debug("hsync start detected")
                h = RGBHsync(self.vsync.value)
                h.expected_length = hsync_expected_length
                self.col_cnt = 0
            if self.hsync_last and not self.hsync.value and self.vsync_last:
                self.log.debug("hsync end detected")

                if (
                    not 0 == self.col_cnt
                    and not self.img.width == self.col_cnt
                    and self.verification
                ):
                    raise Exception(
                        f"Incorrect number of data valids per row {self.col_cnt}"
                    )
                if not 0 == self.col_cnt:
                    self.row_cnt += 1
                h.end_time(self.vsync.value, self.verification)
                hsync_expected_length = h.length
                if self.first_vsync:
                    self.f.hsync.append(h)
                del h
            if self.first_vsync:
                if self.de.value:
                    self.col_cnt += 1
                    self.f.setdata(self.data.value)

            self.hsync_last = self.hsync.value
            self.vsync_last = self.vsync.value

    async def frame_finished(self):
        while True:
            await RisingEdge(self.clk)
            if self.frame_complete:
                self.log.debug("Frame finished detected")
                break

    async def _edge_sync(self):
        sync_last = 0
        sync_cnt = 0
        t0 = 0
        t1 = 0
        t2 = 0
        t_last = 0
        while True:
            await RisingEdge(self.clk)
            if 1 == self.vsync.value and 0 == sync_last:
                t0 = get_sim_time("fs")
                t2 = t0 - t1
                if sync_cnt > 1:
                    self.log.debug(f"Sync edge detected, {get_sim_time('step')}")
                if sync_cnt == 2:
                    self.measure_frequency = 1e15 / t2
                    self.log.info(f"Measured Frequency: {self.measure_frequency} Hz")
                    if self.expected_frequency is not None:
                        if not (
                            (self.expected_frequency - 2)
                            <= self.measure_frequency
                            <= (self.expected_frequency + 2)
                        ):
                            pass
                #                             raise Exception(
                #                                 f"Doesn't match expected frequency {self.expected_frequency} Hz"
                #                             )

                if sync_cnt > 2:
                    if not (t_last - self.clk_time) <= t2 <= (t_last + self.clk_time):
                        raise Exception(f"Sync Period has changed, {t2} {t_last}")
                sync_cnt += 1
            sync_last = self.vsync.value
            t1 = t0
            t_last = t2
