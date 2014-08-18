#!/usr/bin/python

import serial
import time
import requests
import threading
import sys
import Queue
import collections
import ConfigParser
import pickle
import signal
import io

#This is debugging code that dumps a stack trace every 5s
import stacktracer
stacktracer.trace_start("/tmp/trace.html")

from termcolor import colored

### SETTINGS ###
try:
	Config = ConfigParser.ConfigParser()
	Config.read(sys.argv[1])

	ServerUrl = Config.get('GeneralSettings', 'ServerUrl')
	ShortUrl = Config.get('GeneralSettings', 'ShortUrl')
	JpegUrl = Config.get('GeneralSettings', 'JpegUrl')

	SerialDevice = Config.get('DisplaySettings', 'SerialDevice')
	BaudRate = Config.getint('DisplaySettings', 'BaudRate')
	StartMessage = Config.get('DisplaySettings', 'StartMessage') + " " + ShortUrl
	MaxMessages = Config.getint('DisplaySettings', 'MaxMessages')
	ShowStartMessage = Config.getboolean('DisplaySettings', 'ShowStartMessage')
	MessageListStore = Config.get('DisplaySettings', 'MessageListStore')
except Exception, e:
	print "Could not read config file: " + str(e)
	sys.exit(-1)

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

def RemoveNonAscii(s):
	return "".join(i for i in s if ord(i)<128)

class TimeoutError(Exception): pass

def timelimit(timeout):
    def internal(function):
        def internal2(*args, **kw):
            class Calculator(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None
                
                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()[0]
            
            c = Calculator()
            c.start()
            c.join(timeout)
            if c.isAlive():
                raise TimeoutError
            if c.error:
                raise c.error
            return c.result
        return internal2
    return internal

# Send the Message char per char to the display
# Don't send the string at once, it's to fast for the display
def SendToDisplay(Message):
	for c in str(Message):
		SerialPort.write(c)

	# Confirm the new Message
	SerialPort.write(Special.Enter)

def ShowMessages():
	while True:
		# Make a local copy because the list be changed by the main thread,
		# reverse the list because we want the newest messages first.
		#Messages = list(reversed(MessageList))		
		#if ShowStartMessage:
		#	Messages.append(StartMessage)

		# Print every message ...
		#for Message in Messages:
		#	SendToDisplay(Message)
		#	#print colored(Message, "yellow")
		#	time.sleep(15)
		SendToDisplay(Text)
		time.sleep(60)

@timelimit(15)
def StreamJpeg():
	# First download the image from JpegUrl, 5s timeout
	try:
		JpegReq = requests.get(JpegUrl, stream=True, timeout=5, headers={'Connection':'close'})
		JpegReq.raise_for_status()	# Raise an exception if the status code != 200

		# Read the data in chuncks into the buffer
		JpegData = io.BytesIO()
		for Chunck in JpegReq.iter_content(10*1024):
			if Chunck:
				JpegData.write(Chunck)

		# Rewind buffer
		JpegData.seek(0)
		
	except Exception, e:
		print colored("Could not get livestream image: %s" % e, "red")
		return False;
	else:
		# Then upload the image to ServerUrl
		try:
			Post = requests.post(ServerUrl, files={'live.jpg': JpegData.read()}, timeout=5, headers={'Connection':'close'})
			Post.raise_for_status()
			return True;
		except Exception, e:
			print colored("Could not upload livestream image: %s" % e, "red")
			return False

def LiveStream():
	# Default sleep between images
	DefaultSleep = 0.5

	while True:
		try:
			if StreamJpeg():
				Sleep = DefaultSleep
			else:
				Sleep = 10 # Sleep a bit longer

			time.sleep(Sleep)
		except:
			return

def SaveMessageList():
	pickle.dump(MessageList, open(MessageListStore, "wb"))

def SignalHandler(signal, frame):
	print('Bye bye!')
	sys.exit(0)

# Register CTRL-C handler
signal.signal(signal.SIGINT, SignalHandler)

# Maximum x messages in deque
# A deque is a special list: if you add more then the max allowed items, older items are removed.
# This way we always have the x newest messages

try:
	MessageList = pickle.load(open(MessageListStore, "rb"))		#Try to load the deque from file
except:
	MessageList = collections.deque(maxlen=MaxMessages)

Text = ""

# Open serial port
SerialPort = serial.Serial(SerialDevice, BaudRate, bytesize=8, parity='E', stopbits=1, timeout=None)

LiveStreamThread = threading.Thread()
ShowMessagesThread = threading.Thread()

# Endless loop: end the program with CTRL-C
while True:
	if not LiveStreamThread.isAlive():
		print "Starting LiveStream thread"
		try:
			LiveStreamThread = threading.Thread(target=LiveStream)		# Start LiveStream thread
			LiveStreamThread.daemon = True		#This makes sure the program can exit
			LiveStreamThread.start()
		except Exception, e:
			print e

	if not ShowMessagesThread.isAlive():
		print "Starting ShowMessages thread"
		try:
			ShowMessagesThread = threading.Thread(target=ShowMessages)	# Start ShowMessages thread
			ShowMessagesThread.daemon = True	#This makes sure the program can exit
			ShowMessagesThread.start()
		except Exception, e:
			print e

	# Default sleep between requests
	DefaultSleep = 0.5

	# Request new messages from server, 5s timeout
	try:
		DataRequest = requests.get(ServerUrl + "?messages", timeout=5, headers={'Connection':'close'})
		DataRequest.raise_for_status()	# Raise an exception if the status code != 200
		Sleep = DefaultSleep
	except Exception, e:
		print colored("Could not get messages: %s" % e, "red")
		Sleep = 60
	else:
		Data = DataRequest.text
		# Add them to the MessageList, if there are any
		if Data.strip() != "":
			Messages = Data.strip().split("\n")
			Messages = [ RemoveNonAscii(Message) for Message in Messages ]
			MessageList.extend(Messages)
			for Message in Messages:		
				print colored(Message, "yellow")
			SaveMessageList()

			if ShowStartMessage:
				Text = StartMessage			

			for Message in list(reversed(MessageList)):
				Text += Special.WipeCenter				
				Text += Message

	# We have to sleep a bit or we will be using 100% CPU
	time.sleep(Sleep)
