#!/usr/bin/python

import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Example 1
ba = bytearray([0xf1, 				# Leading code
				0x00, 0x00, 		# Locked code
				0x01, 				# Message mode
				0x9e, '1', 			# Lowest speed
				0x84, 'A', 			# Appear 'A'
				0xa0, 'B', 0xa0,  	# Flash 'B'
				0x9f, 				# Start Fat
				'C', 				# 'C'
				0xa0, 'D', 0xa0, 	# Flash 'D'
				0x9f, 				# End Fat
				0x91, 				# Pause
				0xf0, 0xff])		# End code
ser.write(ba)
ser.close()
