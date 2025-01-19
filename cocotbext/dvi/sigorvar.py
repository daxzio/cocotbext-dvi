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

from cocotb.handle import ModifiableObject


class SignalOrVariable:
    def __init__(self, signal=None):
        if signal is None:
            self.signal = False
        else:
            self.signal = signal

    def setimmediatevalue(self, value):
        if isinstance(self.signal, ModifiableObject):
            self.signal.setimmediatevalue(value)
        else:
            self.signal = value

    @property
    def value(self):
        if isinstance(self.signal, ModifiableObject):
            return self.signal.value
        else:
            return self.signal

    @value.setter
    def value(self, value):
        if isinstance(self.signal, ModifiableObject):
            self.signal.value = value
        else:
            self.signal = value
