from machine import Pin
from busio import I2C as Adafruit_I2C
from qwiic_i2c import MicroPythonI2C
from machine import I2C

class I2C_Bus_Impl(Adafruit_I2C, MicroPythonI2C):
    def __init__(self, i2c_bus: I2C, address_xor: int):
        """Initialization"""
        Adafruit_I2C.__init__(self, i2c_bus)
        MicroPythonI2C.__init__(self, i2c_bus)
        self.i2c_bus = i2c_bus
        self.address_xor = address_xor

    def deinit(self):
        """Deinitialization"""
        try:
            del self._i2c
        except AttributeError:
            pass

    def convertAddress(self, address: int):
            return address ^ self.address_xor

class I2C_Bus:
    __FREQUENCY = 100000
    __NO_ADDRESS_XOR = 0x00
    __DEFAULT_ADDRESS_XOR = 0x40

    __i2c_left = None
    __i2c_right = None

    __I2C_top_left = None
    __I2C_top_right = None
    __I2C_bottom_left = None
    __I2C_bottom_right = None

    @classmethod
    def __getLeftI2CBus(cls) -> I2C:
        if cls.__i2c_left is None:
            cls.__i2c_left = I2C(id=0, sda=Pin(4), scl=Pin(5), freq=cls.__FREQUENCY)
        return cls.__i2c_left

    @classmethod
    def __getRightI2CBus(cls) -> I2C:
        if cls.__i2c_right is None:
            cls.__i2c_right = I2C(id=1, sda=Pin(38), scl=Pin(39), freq=cls.__FREQUENCY)
        return cls.__i2c_right

    @classmethod
    def I2C_OBEN_LINKS(cls) -> I2C_Bus_Impl:
        if cls.__I2C_top_left is None:
            cls.__I2C_top_left = I2C_Bus_Impl(cls.__getLeftI2CBus(), cls.__NO_ADDRESS_XOR)
        return cls.__I2C_top_left

    @classmethod
    def I2C_OBEN_RECHTS(cls) -> I2C_Bus_Impl:
        if cls.__I2C_top_right is None:
            cls.__I2C_top_right = I2C_Bus_Impl(cls.__getRightI2CBus(), cls.__NO_ADDRESS_XOR)
        return cls.__I2C_top_right

    @classmethod
    def I2C_UNTEN_LINKS(cls) -> I2C_Bus_Impl:
        if cls.__I2C_bottom_left is None:
            cls.__I2C_bottom_left = I2C_Bus_Impl(cls.__getLeftI2CBus(), cls.__DEFAULT_ADDRESS_XOR)
        return cls.__I2C_bottom_left

    @classmethod
    def I2C_UNTEN_RECHTS(cls) -> I2C_Bus_Impl:
        if cls.__I2C_bottom_right is None:
            cls.__I2C_bottom_right = I2C_Bus_Impl(cls.__getRightI2CBus(), cls.__DEFAULT_ADDRESS_XOR)
        return cls.__I2C_bottom_right
