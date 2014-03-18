#!/usr/bin/python

import serial

ser = serial.Serial('/dev/ttyUSB1', 2400, timeout=1)
fil = open('dump', 'w')


text = "Hello World!"
text += (80-len(text)) * " "
text += "\r"

ser.write(text)
fil.write(text)

ser.close()
fil.close()
