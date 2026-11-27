#-----------------------------------------------------------------------------
# micropython_i2c.py
#
# Encapsulate MicroPython port I2C interface
#------------------------------------------------------------------------
#
# Written by  oclyke, Feb 2021
# Modified to remove abstraction layers: Tom Markuske, Sep 2025
# 
#
# More information on qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#
#==================================================================================
# Copyright (c) 2021 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#==================================================================================

import sys
from machine import I2C

_PLATFORM_NAME = "MicroPython"

#-------------------------------------------------
# Exported method to get the I2C driver for the execution plaform. 
#
# If no driver is found, a None value is returned
def getI2CDriver():
	"""
	.. function:: getI2CDriver()

		Returns the qwiic I2C driver object for current platform.

		:return: A qwiic I2C driver object for the current platform.
		:rtype: object

		:example:

		>>> import qwiic_i2c
		>>> i2cDriver = qwiic_i2c.getI2CDriver()
		>>> myData = i2cDriver.readByte(0x73, 0x34)
	"""

	driver = MicroPythonI2C()
	return driver

def get_i2c_driver():
	"""
	.. function:: get_i2c_driver()

		Returns the qwiic I2C driver object for current platform.

		:return: A qwiic I2C driver object for the current platform.
		:rtype: object

		:example:

		>>> import qwiic_i2c
		>>> i2cDriver = qwiic_i2c.get_i2c_driver()
		>>> myData = i2cDriver.readByte(0x73, 0x34)
	"""
	return getI2CDriver()


class MicroPythonI2C:
	name = _PLATFORM_NAME
	_i2cbus = None

	def __init__(self, i2c_bus: I2C):
		self._i2cbus = i2c_bus

	# def __init__(self, sda=None, scl=None, freq=100000):
	# 	raise AttributeError("Not implemented. Use I2C_Bus class instead.")

	@classmethod
	def isPlatform(cls):
		""" 
			Called to determine if the specific driver supports the current platorm

			:return: True if this platform is supported, otherwise False
			:rtype: bool

		"""
		try:
			return 'micropython' in sys.implementation
		except:
			return False

	@classmethod
	def is_platform(cls):
		""" 
			Called to determine if the specific driver supports the current platorm

			:return: True if this platform is supported, otherwise False
			:rtype: bool

		"""
		return cls.isPlatform()

	#-------------------------------------------------------------------------		
	# read Data Command

	def readWord(self, address, commandCode):
		""" 
			Called to read a word (16 bits) from a specific device.

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from, or `None` for no command

			:return: Returns the read data
			:rtype: integer - first 16 bits contain the read data. 

		"""
		if (commandCode == None):
			buffer = self._i2cbus.readfrom(address, 2)
		else:
			buffer = self._i2cbus.readfrom_mem(address, commandCode, 2)

		return (buffer[1] << 8 ) | buffer[0]

	def read_word(self, address, commandCode):
		""" 
			Called to read a word (16 bits) from a specific device.

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from, or `None` for no command

			:return: Returns the read data
			:rtype: integer - first 16 bits contain the read data. 

		"""
		return self.readWord(address, commandCode)

	def readByte(self, address, commandCode = None):
		""" 
			Called to read a byte (8 bits) from a specific device.

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from, or `None` for no command

			:return: Returns the read data
			:rtype: integer - first 8 bits contain the read data. 

		"""
		if (commandCode == None):
			return self._i2cbus.readfrom(address, 1)[0]

		return self._i2cbus.readfrom_mem(address, commandCode, 1)[0]

	def read_byte(self, address, commandCode = None):
		""" 
			Called to read a byte (8 bits) from a specific device.

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from, or `None` for no command

			:return: Returns the read data
			:rtype: integer - first 8 bits contain the read data. 

		"""
		return self.readByte(address, commandCode)

	def readBlock(self, address, commandCode, nBytes):
		""" 
			Called to read a block of bytesfrom a specific device.

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from, or `None` for no command
			:param nBytes: The number of bytes to read from the device

			:return: Returns the read data as a list of integers.
			:rtype: list 

		"""
		if (commandCode == None):
			return self._i2cbus.readfrom(address, nBytes)

		return self._i2cbus.readfrom_mem(address, commandCode, nBytes)

	def read_block(self, address, commandCode, nBytes):
		""" 
			Called to read a block of bytesfrom a specific device.

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from, or `None` for no command
			:param nBytes: The number of bytes to read from the device

			:return: Returns the read data as a list of integers.
			:rtype: list 

		"""
		return self.readBlock(address, commandCode, nBytes)

	#--------------------------------------------------------------------------	
	# write Data Commands 
	#
	# Send a command to the I2C bus for this device. 
	#
	# value = 16 bits of valid data..
	#

	def writeCommand(self, address, commandCode):
		""" 
			Called to write a command to a device. No actual data is written

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from 

			:return: None

		"""
		self._i2cbus.writeto(address, commandCode.to_bytes(1, 'little'))

	def write_command(self, address, commandCode):
		""" 
			Called to write a command to a device. No actual data is written

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from 

			:return: None

		"""
		return self.writeCommand(address, commandCode)

	def writeWord(self, address, commandCode, value):
		""" 
			Called to write a word (16 bits) to a device. 

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from
			:param value: The word (16 bits) to write to the I2C bus

			:return: None

		"""
		self._i2cbus.writeto_mem(address, commandCode, value.to_bytes(2, 'little'))

	def write_word(self, address, commandCode, value):
		""" 
			Called to write a word (16 bits) to a device. 

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from
			:param value: The word (16 bits) to write to the I2C bus

			:return: None

		"""
		return self.writeWord(address, commandCode, value)

	def writeByte(self, address, commandCode, value):
		""" 
			Called to write a byte (8 bits) to a device. 

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from
			:param value: The byte (8 bits) to write to the I2C bus

			:return: None

		"""
		self._i2cbus.writeto_mem(address, commandCode, value.to_bytes(1, 'little'))

	def write_byte(self, address, commandCode, value):
		""" 
			Called to write a byte (8 bits) to a device. 

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from
			:param value: The byte (8 bits) to write to the I2C bus

			:return: None

		"""
		return self.writeByte(address, commandCode, value)

	def writeBlock(self, address, commandCode, value):
		""" 
			Called to write a block of bytes to a device. 

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from
			:param value: A list of bytes (ints) to write on the I2C bus.

			:return: None

		"""
		self._i2cbus.writeto_mem(address, commandCode, bytes(value))

	def write_block(self, address, commandCode, value):
		""" 
			Called to write a block of bytes to a device. 

			:param address: The I2C address of the device to read from
			:param commandCode: The "command" or register to read from
			:param value: A list of bytes (ints) to write on the I2C bus.

			:return: None

		"""
		return self.writeBlock(address, commandCode, value)

	def writeReadBlock(self, address, writeBytes, readNBytes):
		""" 
			Called to write a block of bytes to a device, send no stop bit, and then read a block of bytes.

			:param address: The I2C address of the device to read from
			:param writeBytes: A list of bytes (ints) to write on the I2C bus.
			:param readNBytes: The number of bytes to read from the device

			:return: A list of bytes read from the device.
			:rtype: list

		"""
		# micropython I2C doesn't have a corresponding "i2c_rdwr" function like smbus2, so we will make our own by passing stop=False to not send stop bits between repeated transfers
		self._i2cbus.writeto(address, bytes(writeBytes), False)
		return self._i2cbus.readfrom(address, readNBytes)
	
	def write_read_block(self, address, writeBytes, readNBytes):
		""" 
			Called to write a block of bytes to a device, send no stop bit, and then read a block of bytes.

			:param address: The I2C address of the device to read from
			:param writeBytes: A list of bytes (ints) to write on the I2C bus.
			:param readNBytes: The number of bytes to read from the device

			:return: A list of bytes read from the device.
			:rtype: list

		"""
		return self.writeReadBlock(address, writeBytes, readNBytes)

	def isDeviceConnected(self, devAddress):
		"""
			Determines if a particular device (at the provided address)
			is connected to the bus.

			:param devAddress: The I2C address of the device to check

			:return: True if the device is connected, otherwise False.
			:rtype: bool

		"""
		isConnected = False
		try:
			# Try to write nothing to the device
			# If it throws an I/O error - the device isn't connected
			self._i2cbus.writeto(devAddress, bytearray())
			isConnected = True
		except:
			pass
		
		return isConnected

	def is_device_connected(self, devAddress):
		"""
			Determines if a particular device (at the provided address)
			is connected to the bus.

			:param devAddress: The I2C address of the device to check

			:return: True if the device is connected, otherwise False.
			:rtype: bool

		"""
		return self.isDeviceConnected(devAddress)

	def ping(self, devAddress):
		"""
			Determines if a particular device (at the provided address)
			is connected to the bus.

			:param devAddress: The I2C address of the device to check

			:return: True if the device is connected, otherwise False.
			:rtype: bool

		"""
		return self.isDeviceConnected(devAddress)

    # same as busio:
	def scan(self):
		"""
			Used to scan the I2C bus, returning a list of I2C address attached to the computer.

			:return: A list of I2C addresses. If no devices are attached, an empty list is returned.
			:rtype: list

		"""
		return self._i2cbus.scan()

	#-------------------------------------------------------------------------	
	# stubs to support Python with statements. 
	#
	# Helpful for I2C interactions that require a mutex.

    # same as busio:
	def __enter__(self):
		return self

    # same as busio:
	def __exit__(self, type, value, traceback):
		pass
