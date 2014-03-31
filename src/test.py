#!/usr/bin/python

import serial
import time

class Special:
	#Use these before text
	ScrollLeft 	= bytearray({0})
	ScrollRight = bytearray({1})
	ScrollUp	= bytearray({2})
	ScrollDown	= bytearray({3})
	Appear		= bytearray({4})
	JumpOn		= bytearray({5})
	OpenLeft	= bytearray({6})
	OpenRight	= bytearray({7})
	OpenUp		= bytearray({8})
	OpenDown	= bytearray({9})
	OpenCenter	= bytearray({10})
	OpenEdges	= bytearray({11})

	#Use these after text
	RotateUp	= bytearray({12})
	#???		= bytearray({13})
	RotateDown	= bytearray({14})
	ScrollUp	= bytearray({15})
	EndScrDown	= bytearray({16})	
	WipeLeft	= bytearray({19})
	WipeRight	= bytearray({20})
	WipeUp		= bytearray({21})
	WipeDown	= bytearray({22})
	WipeCenter	= bytearray({23})
	WipeEdges	= bytearray({24})

	#Control signals
	Clear		= bytearray({17})
	Pause		= bytearray({18})

	End			= bytearray({25})
	Clock		= bytearray({26})
	Halt		= bytearray({27})
	Speed		= bytearray({28})

	#Markup
	Fat			= bytearray({29})
	Flash		= bytearray({30})

def Speed(Val):
	if Val < 0 or Val > 5:
		raise Exception("Invalid speed")
	return Special.Speed + str(Val)

ser = serial.Serial('/dev/ttyUSB0', 2400, bytesize=8, parity='E', stopbits=1, timeout=None)

text = ""
text += Special.OpenEdges
text += "ELECTRONICS:LAB"
text += Special.Pause + Special.Pause
text += Special.WipeUp
text += " elke maandag van 18u-21u"
text += Special.RotateDown
text += Special.Pause + Special.Pause
text += Special.Clock
text += Special.Pause + Special.Pause + Special.Pause	

for c in str(text):
	ser.write(c)

ser.write("\r")

ser.close()
