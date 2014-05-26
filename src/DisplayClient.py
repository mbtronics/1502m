#!/usr/bin/python

import serial
import time
import requests
import thread
import sys
import Queue
import collections
import ConfigParser
from termcolor import colored

### SETTINGS ###
Config = ConfigParser.ConfigParser()
Config.read("DisplayClient.conf")

ServerUrl = Config.get('GeneralSettings', 'ServerUrl')
ShortUrl = Config.get('GeneralSettings', 'ShortUrl')
JpegUrl = Config.get('GeneralSettings', 'JpegUrl')

SerialDevice = Config.get('DisplaySettings', 'SerialDevice')
BaudRate = Config.getint('DisplaySettings', 'BaudRate')
StartMessage = Config.get('DisplaySettings', 'StartMessage') + " " + ShortUrl
MaxMessages = Config.getint('DisplaySettings', 'MaxMessages')
ShowStartMessage = Config.getboolean('DisplaySettings', 'ShowStartMessage')
################

print "Welcome to the 1502m Message Display client"
print "-------------------------------------------"
print "Message Server: " + ServerUrl
print "Short URL: " + ShortUrl
print "Livestream JPEG URL: " + JpegUrl
print "Connecting to LED display on " + SerialDevice + " at " + str(BaudRate) + " baud"
print "Maximum " + str(MaxMessages) + " messsages in queue"
print "Start message: " + StartMessage
print "Show start message? " + str(ShowStartMessage)
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
		if ShowStartMessage:
			Messages.append(StartMessage)

		# Print every message ...
		for Message in Messages:
			SendToDisplay(Message)
			print colored(Message, "yellow")
			time.sleep(15)

def LiveStream():
	# Default sleep between images
	DefaultSleep = 0.5

	while 1:
		# First download the image from JpegUrl, 5s timeout
		try:
			JpegData = requests.get(JpegUrl, stream=True, timeout=5)
			JpegData.raise_for_status()	# Raise an exception if the status code != 200
		except Exception, e:
			print colored("Could not get livestream image: %s" % e, "red")
			Sleep = 10 # Sleep a bit longer
		else:
			# Then upload the image to ServerUrl
			try:
				requests.post(ServerUrl, files={'live.jpg': JpegData.raw.read()})
				Sleep = DefaultSleep # Everything went ok, do the short sleep
			except Exception, e:
				print colored("Could not upload livestream image: %s" % e, "red")
				Sleep = 10 # Sleep a bit longer

		time.sleep(Sleep)

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
	# Default sleep between requests
	DefaultSleep = 0.5

	# Request new messages from server, 5s timeout
	try:
		DataRequest = requests.get(ServerUrl + "?messages", timeout=5)
		DataRequest.raise_for_status()	# Raise an exception if the status code != 200
		Sleep = DefaultSleep
	except Exception, e:
		print colored("Could not get messages: %s" % e, "red")
		Sleep = 10
	else:
		Data = DataRequest.text
		# Add them to the MessageList, if there are any
		if Data.strip() != "":
			MessageList.extend(Data.strip().split("\n"))

	# We have to sleep a bit or we will be using 100% CPU
	time.sleep(Sleep)
