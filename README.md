# DVI and RGB interface modules for Cocotb

[![Build Status](https://github.com/daxzio/cocotbext-dvi/actions/workflows/regression-tests.yml/badge.svg?branch=main)](https://github.com/daxzio/cocotbext-dvi/actions/)
[![PyPI version](https://badge.fury.io/py/cocotbext-dvi.svg)](https://pypi.org/project/cocotbext-dvi)
[![Downloads](https://pepy.tech/badge/cocotbext-dvi)](https://pepy.tech/project/cocotbext-dvi)

GitHub repository: https://github.com/daxzio/cocotbext-dvi

## Introduction

DVI and RGB simulation models for [cocotb](https://github.com/cocotb/cocotb).

## Installation

Installation from pip (release version, stable):

    $ pip install cocotbext-dvi

Installation from git (latest development version, potentially unstable):

    $ pip install https://github.com/daxzio/cocotbext-dvi/archive/master.zip

Installation for active development:

    $ git clone https://github.com/daxzio/cocotbext-dvi
    $ pip install -e cocotbext-dvi

## Documentation and usage examples

See the `tests` directory for complete testbenches using these modules.

## RGB

It is important to understand that DVI is a serially encoded version of 24-bit RGB or sometimes called RGB888.

RGB888 is a color encoding system that represents colors using a combination of red, green, and blue components, each of which has 8 bits of information. This means that there are 256 possible values for each component, resulting in a total of 16,777,216 possible color combinations.

Typically, due to the high speed of DVI, most digitial designs will convert to 24 bit RGB to use internally, or if transmitting generte images as RGB before being converted to DVI on the TX pins.

As such there is a fully functionally RGB interfaces (Driver and Sink) in this module.  They are actually used by the module to generate the DVI Driver and Sink too.

### RGB Bus

The `RGBBus` is used to map to a RGB interface on the `dut`.  These hold instances of bus objects for the individual channels, which are currently extensions of `cocotb_bus.bus.Bus`.  Class methods `from_entity` and `from_prefix` are provided to facilitate signal default name matching. 

#### Required:
* _vsync_
* _hsync_
* _de_
* _data_

#### Optional:
* _vblank_
* _hblank_
* _field_id_

#### Example

```python
from cocotbext.dvi import RGBBus
rgb_in_bus = RGBBus.from_prefix(dut, prefix="vid_in")
```

or 
    
```python
signals_in = {
    "vsync": "vid_in_vsync",
    "hsync": "vid_in_hsync",
    "de": "vid_in_de",
    "data": "vid_in_data",
}
rgb_in_bus = RGBBus(dut, signals=signals_in)
```

### RGB Driver

The `RGBDriver` class implement a RGB driver and is capable of generating RGB888 signals to be supplied to a RGB input.

```python
from cocotbext.dvi import RGBBus, RGBDriver
rgb_in_bus = RGBBus.from_prefix(dut, prefix="vid_in")
rgb_in = RGBDriver(
    dut.clk,
    rgb_in_bus,
    image_file="./images/320x240.bmp",
)
```

* _frequency_: Frame frequency images, default `60` Hz
* _height_: Truncated image height, use this height instead if image height is positive, default `-1`
* _width_: Truncated image width, use this width instead if image width is positive, default `-1`
* _logging_enabled_: Logging enable, default `True`

#### Methods

* `await_start()`: Return when an image has begun (if already begun return immediatly)
* `await_image(num)`: Return then a full number of image, `num`, image, frames, has been complete. `num` default `1`  

### RGB Sink

The `RGBSink` class implement a RGB sink and is capable of receiving RGB888 signals, decoding it to image data, vsync, hsync and comparing it against a supplied image, `image_file.`

```python
from cocotbext.dvi import RGBBus, RGBSink
rgb_out_bus = RGBBus.from_prefix(dut, prefix="vid_out")
rgb_out = RGBSink(
    dut.clk,
    rgb_out_bus,
    image_file="./images/320x240.bmp",
)
```

* _image_file_: Image to compare receoved against. Raise error is there is a mismatch in image content but also column and row counts, default `None` (no comparison)
* _expected_frequency_: Frame frequency images, default `60` Hz
* _height_: Truncated image height, use this height instead if image height is positive, default `-1`
* _width_: Truncated image width, use this width instead if image width is positive, default `-1`
* _logging_enabled_: Logging enable, default `True`
* _clk_freq_: Test receveied clock frequency, default `25.0` Mhz

#### Methods

* `frame_finished(num)`: Return then a full number of image, `num`, image, frames, has been received. `num` default `1` 

## DVI

DVI, Digitial Visual Interface, is the video interface format used in HDMI. It is comprised of a low speed clock, Pixel Clock, and a high speed (5x) data channel, TMDS Clock, typically 3 bits wide (one channel for each color, RGB).  Both the clock and the data signals are differentially encoded for EMI purposes. In simulation land this is redundant, however the module can supply and/or detect differential signals on the DVI bus.  

Pixel or RGB data is the source, each clock cycle generates 1 pixel, or 8 bits of data per color. This is RGB888.  Each color has one differential pair on the data channel for transmission. 

The 8 bits of the color  are encoded  using the [TMDS](https://en.wikipedia.org/wiki/Transition-minimized_differential_signaling), which generated 10 bits of data. These 10 bits are transmit on both edges of a generated clock, which is 5X faster than the clock being TX as part of the interface.

There are two key clock signals:

 * **Pixel Clock**: This clock determines the rate at which pixels are sent.   
 * **TMDS Clock**: This is the high-speed clock used to transmit the encoded data over the TMDS channels.

The relationship between these clocks is tied to the TMDS encoding process. Here's how it works:

 * **TMDS Encoding**: TMDS takes 8-bit RGB data and encodes it into 10-bit data.   
 * **Serialization and Transmission**: These 10 bits are then serialized and transmitted over the TMDS channels.

This version of the DVI Driver is wrapped around the RGB Driver. Simiarly DVI Sink is also wrapped around RGB Sink. 

### DVI Bus

The `DVIBus` is used to map to a DVI interface on the `dut`.  These hold instances of bus objects for the individual channels, which are currently extensions of `cocotb_bus.bus.Bus`.  Class methods `from_entity` and `from_prefix` are provided to facilitate signal default name matching. 

#### Required:
* _clk_p_
* _data_p_

#### Optional:
* _clk_n_
* _data_n_

#### Example

```python
from cocotbext.dvi import DVIBus
dvi_in_bus = DVIBus.from_prefix(dut, prefix="tmds_in")
```

or 
    
```python
from cocotbext.dvi import DVIBus
signals_in = {
    "clk_p": "tmds_in_clk_p",
    "clk_n": "tmds_in_clk_n",
    "data_p": "tmds_in_data_p",
    "data_n": "tmds_in_data_n",
}
dvi_in_bus = DVIBus(dut, signals=signals_in)
```

### DVI Driver

```python
from cocotbext.dvi import DVIBus, DVIDriver
dvi_in_bus = DVIBus.from_prefix(dut, prefix="tmds_in")
dvi_in = DVIDriver(
    dut,
    dvi_in_bus,
    image_file="./images/320x240.bmp",
)
```
* _frequency_: Frame frequency images, default `60` Hz
* _height_: Truncated image height, use this height instead if image height is positive, default `-1`
* _width_: Truncated image width, use this width instead if image width is positive, default `-1`
* _logging_enabled_: Logging enable, default `True`

#### Methods

* `await_start()`: Return when an image has begun (if already begun return immediatly)
* `await_image(num)`: Return then a full number of image, `num`, image, frames, has been complete. `num` default `1`  


### DVI Sink

```python
from cocotbext.dvi import DVIBus, DVISink
dvi_out_bus = DVIBus.from_prefix(dut, prefix="tmds_out")
dvi_out = DVISink(
    dut,
    dvi_out_bus,
    image_file="./images/320x240.bmp",
)
```
* _image_file_: Image to compare receoved against. Raise error is there is a mismatch in image content but also column and row counts, default `None` (no comparison)
* _expected_frequency_: Frame frequency images, default `60` Hz
* _height_: Truncated image height, use this height instead if image height is positive, default `-1`
* _width_: Truncated image width, use this width instead if image width is positive, default `-1`
* _logging_enabled_: Logging enable, default `True`
* _clk_freq_: Test receveied clock frequency, default `25.0` Mhz

#### Methods

* `frame_finished(num)`: Return then a full number of image, `num`, image, frames, has been received. `num` default `1` 


