# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`busio` - Bus protocol support like I2C and SPI
=================================================

See `CircuitPython:busio` in CircuitPython for more details.

* Author(s): cefn, modified by Tom Markuske to consolidate different I2C APIs and to only support generic Micropython instead of CircuitPython
"""
from machine import I2C

class I2C:
    """
    Busio I2C Class for CircuitPython Compatibility. Used
    for both MicroPython and Linux.

    NOTE: Frequency has no effect on Linux systems. The argument is only there for compatibility.
    """

    def __init__(self, i2c_bus: I2C):
        self._i2c = i2c_bus

    # def __init__(self, scl, sda, frequency=100000):
    #     raise AttributeError("Not implemented. Use I2C_Bus class instead.")

    def init(self, scl, sda, frequency):
        raise AttributeError("Not implemented. Use I2C_Bus class instead.")

    def deinit(self):
        """Deinitialization"""
        try:
            raise AttributeError("Not implemented. Use I2C_Bus class instead.")
        except AttributeError:
            pass

    # same as qiic_i2c:
    def scan(self):
        """Scan for attached devices"""
        return self._i2c.scan()

    def readfrom_into(self, address, buffer, *, start=0, end=None):
        """Read from a device at specified address into a buffer"""
        if start != 0 or end is not None:
            if end is None:
                end = len(buffer)
            buffer = memoryview(buffer)[start:end]
        return self._i2c.readfrom_into(address, buffer, True)

    def writeto(self, address, buffer, *, start=0, end=None):
        """Write to a device at specified address from a buffer"""
        if isinstance(buffer, str):
            buffer = bytes([ord(x) for x in buffer])
        if start != 0 or end is not None:
            if end is None:
                return self._i2c.writeto(address, memoryview(buffer)[start:], True)
            return self._i2c.writeto(address, memoryview(buffer)[start:end], True)
        return self._i2c.writeto(address, buffer, True)

    def writeto_then_readfrom(
        self,
        address,
        buffer_out,
        buffer_in,
        *,
        out_start=0,
        out_end=None,
        in_start=0,
        in_end=None,
        stop=False,
    ):
        """Write data from buffer_out to an address and then
        read data from an address and into buffer_in
        """
        if out_end:
            self._i2c.writeto(address, buffer_out[out_start:out_end], stop)
        else:
            self._i2c.writeto(address, buffer_out[out_start:], stop)

        if not in_end:
            in_end = len(buffer_in)
        read_buffer = memoryview(buffer_in)[in_start:in_end]
        self._i2c.readfrom_into(address, read_buffer, stop)

    #-------------------------------------------------------------------------	
    # stubs to support Python with statements. 
    #
    # Helpful for I2C interactions that require a mutex.

    # same as qiic_i2c:
    def __enter__(self):
        return self

    # same as qiic_i2c:
    def __exit__(self, type, value, traceback):
        pass
