#!/usr/bin/python

import serial
import time
import requests
import thread
import sys
import Queue
import collections

### SETTINGS ###
ServerUrl = "http://185.27.174.114/1502m/src/webpage/MessageServer.php"
ShortUrl = "http://tinyurl.com/BudaCam"
JpegUrl = "http://10.0.0.15/live.jpg"
SerialDevice = "/dev/ttyUSB0"
BaudRate = 2400
StartMessage = "Post uw bericht op " + ShortUrl
MaxMessages = 3
################

print "Welcome to the 1502m Message Display client"
print "-------------------------------------------"
print "Message Server: " + ServerUrl
print "Short URL: " + ShortUrl
print "Livestream JPEG URL: " + JpegUrl
print "Connecting to LED display on " + SerialDevice + " at " + str(BaudRate) + " baud"
print "Maximum " + str(MaxMessages) + " messsages in queue"
print

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
	Enter		= bytearray({13})
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

# Send the Message char per char to the display
# Don't send the string at once, it's to fast for the display
def SendToDisplay(Message):
	for c in str(Message):
		SerialPort.write(c)

	# Confirm the new Message
	SerialPort.write(Special.Enter)

def ShowMessages():
	while 1:
		# Make a local copy because the list be changed by the main thread,
		# reverse the list because we want the newest messages first.
		Messages = list(reversed(MessageList))
		Messages.append(StartMessage)

		# Print every message ...
		for Message in Messages:
			SendToDisplay(Message)
			print Message
			time.sleep(5)

def LiveStream():
	while 1:
		# First download the image from JpegUrl
		JpegData = requests.get(JpegUrl, stream=True)
		# Then upload the image to ServerUrl
		requests.post(ServerUrl, files={'live.jpg': JpegData.raw.read()})
		time.sleep(0.5)

# Maximum x messages in deque
# A deque is a special list: if you add more then the max allowed items, older items are removed.
# This way we always have the x newest messages
MessageList = collections.deque(maxlen=MaxMessages)

# Open serial port
SerialPort = serial.Serial(SerialDevice, BaudRate, bytesize=8, parity='E', stopbits=1, timeout=None)

# Start ShowMessages thread
thread.start_new_thread(ShowMessages, ())

# Start LiveStream thread
thread.start_new_thread(LiveStream, ())

# Endless loop: end the program with CTRL-C
while True:
	# Request new messages from server
	Data = requests.get(ServerUrl + "?messages").text

	# Add them to the MessageList, if there are any
	if Data.strip() != "":
		MessageList.extend(Data.strip().split("\n"))

	# We have to sleep a bit or we will be using 100% CPU
	time.sleep(1)
