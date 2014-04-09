#!/usr/bin/python

import serial
import time
import requests
import thread
import sys
import Queue

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
	Enter		= bytearray({13})
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

def SendToDisplay(Message):
	for c in str(Message):
		SerialPort.write(c)
	SerialPort.write(Special.Enter)

def GetData():
	while 1:
		Data = requests.get(ServerUrl + "?messages").text
		if Data.strip() != "":
			MessageQueue.put(Data.strip().split("\n"))
		time.sleep(5)

#text = ""
#text += Special.OpenEdges
#text += "ELECTRONICS:LAB"
#text += Special.Pause + Special.Pause
#text += Special.WipeUp
#text += " elke maandag van 18u-21u"
#text += Special.RotateDown
#text += Special.Pause + Special.Pause

#ServerUrl = "http://185.27.174.114/MessageServer.php"
ServerUrl = "http://localhost/src/MessageServer.php"
StartMessage = "Post uw bericht op " + ServerUrl

SerialPort = serial.Serial('/dev/ttyUSB0', 2400, bytesize=8, parity='E', stopbits=1, timeout=None)
MessageQueue = Queue.Queue()
thread.start_new_thread(GetData, ())

while True:
	try:
		NewMessages = MessageQueue.get(True, 10)
		print NewMessages
	except Queue.Empty:
		pass
	except KeyboardInterrupt:
		print "Exiting!"
		SerialPort.close()
		sys.exit()

