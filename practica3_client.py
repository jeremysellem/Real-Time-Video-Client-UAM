from appJar import gui
from PIL import Image, ImageTk
from requests import get
import numpy as np
import cv2, sys
import time, datetime
import socket
import re, operator
import calls as C
import math, threading

class VideoClient(object):
	config = "./config.txt"
	welcomePage = "images/Welcome.gif"
	window_size = "820x600"
	server = "vega.ii.uam.es"
	versions = "V0"
	server_dest_port = 8000
	client_dest_Port = None # We don't know it until we ask the database 
	myReceiverPort = 5100 # Where I want to receive data
	myIP = None
	usersTable = None
	sock = None # Socket with server
	inCall = False # If True this variable blocks access to other buttons than pause, resume and hang up
	currentCall = None
	inPause = False
	secondLog = False

	def stop(self):
		self.errorLog("Program closed")
	
	# Create connection connection with host passed in argument
	def initiateSocket(self):
		try:
			self.sock = socket.create_connection((self.server, self.server_dest_port), 1)
			self.myIP = socket.gethostbyname(socket.gethostname())
		except socket.timeout:
			self.errorLog("Timeout exceeded while attempting to reach server")
			raise socket.error
		except socket.error:
			self.errorLog("Unexpected error while initiating socket")
			raise socket.error
	
	def refreshListUsers(self):
		# Now we try to connect to server
		try:
			self.initiateSocket()
		except socket.error:
			# Unable to initiate a socket
			self.errorLog("Failed to establish connection with DS server")
			self.errorLog("Please check your internet connection, your VPN, server field and server_dest_port field")
			self.errorLog("Failed to refresh list of users")
			return

		# Send the LIST query
		try:
			f = open("users.txt", "w", newline='')
			self.sock.send(bytes("LIST_USERS", 'utf-8'))
			first = True
			while True: # While the datagram is full, means there is more names coming
				response = self.sock.recv(1514).decode('utf-8')
				if response[0:2] != "OK" and first:
					self.errorLog("Server response to LIST_USERS query is " + response)
					self.errorLog("Failed to refresh list of users")
					self.sock.close()
					return None
				else:
					f.write(response)
				if len(response) != 1448:
					break
				first = False
			self.sock.close()
			f.close()
		except(OSError, IOError):
			self.errorLog("Openning or writting in a txt file to store users failed")
			self.errorLog("Failed to refresh list of users")
			self.sock.close()
			return None
		except socket.error:
			self.errorLog("Socket error while refreshing the list of users")
			self.errorLog("Failed to refresh the list")
			self.sock.close()
			return None
		except:
			self.errorLog("Unknown error while refreshing the list of users")
			self.sock.close()
			return None

		# Parse the response to return the users as a list
		try:
			f = open("users.txt", "r")
			temp = f.read()
			temp = temp.split(' ')
			f.close()
		except:
			self.errorLog("Openning or writting in a txt file to store users failed")
			self.errorLog("Failed to refresh list of users")
			self.sock.close()
			return None

		users_count = int(math.floor(len(temp)-3)/3)
		try:
			# Empty the list and fill it with new usernames
			self.usersTable = [''for x in range(users_count)]
			self.usersTable[0] = temp[3]
			for i in range(0,users_count-1):
				self.usersTable[i+1] = temp[6+3*i].split('#')[1]
			
			# We sort the table by alphabetical order
			self.usersTable = sorted(self.usersTable)
			self.errorLog("Refreshed the list of registered users")
			self.sock.close()
			return self.usersTable
		
		except(IndexError):
			self.errorLog("Unable to refresh the list of registered users (IndexError)")

		self.sock.close()
		return None

	def startClient(self):
		# First of all we verify the connection with the server
		if self.sock is None:
			raise socket.error
		
		self.errorLog("Successfully logged in as " + self.username)

		# Now we display the user interface
		self.app = gui("Cliente Multimedia P2P - Redes2", self.window_size)
		self.app.setPadding([0,0])
		self.app.setResizable(canResize=False)
		self.app.setBg("lightgrey", override=True)
		self.app.setFg("black", override=True)
		
		# Components of GUI
		self.app.setStretch("both")
		self.app.setSticky("nesw")

		# Top left corner: display username
		self.app.startFrame("Login", 0, 0, rowspan = 1, colspan = 1)
		self.app.separator()
		self.app.setPadding([0,5])
		self.app.addLabel("L", "Logged as:")
		self.app.setPadding([0,0])
		self.app.addLabel("myUsername", self.username)
		self.app.setLabelWidth("L", 15)
		self.app.setLabelHeight("L", 1)
		self.app.setLabelHeight("myUsername", 1)
		self.app.addHorizontalSeparator(colour=None)
		self.app.stopFrame()

		# Top right corner: display video media
		self.app.startFrame("Stream", 0, 1, rowspan = 3, colspan = 1)
		self.app.addImage("Video", self.welcomePage)
		self.app.setImageWidth("Video", 640)
		self.app.setImageHeight("Video", 480)
		self.app.stopFrame()

		# Left side: list of registered users
		self.app.startFrame("ListUsers", 2, 0, rowspan = 1)
		self.app.addLabel("Users")
		self.app.addListBox("List", self.refreshListUsers())
		self.app.setListBoxBg("List", "lightgrey")
		self.app.setListBoxFg("List", "black")
		self.app.setListBoxHeight("List", 18)
		self.app.addButtons(["Refresh"], self.buttonsCallback)
		self.app.stopFrame()

		# Bottom right corner: buttons needed to manage the app
		self.app.startFrame("Buttons", 3, 0, rowspan = 1, colspan = 2)
		self.app.separator()
		self.app.addButtons(["Call", "Resume", "Pause", "Hang up", "Log out", "Quit"], self.buttonsCallback)
		self.app.stopFrame()
	
		# Add status bar
		self.app.addStatusbar(fields=3)
		self.app.setStatusbarWidth(30, 0)
		self.app.setStatusbarWidth(30, 1)
		self.app.setStatusbar("inCall = {}".format(self.inCall), 2)

		# Set button style
		for b in ["Refresh", "Call", "Resume", "Pause", "Hang up", "Log out", "Quit"]:
			self.app.setButtonRelief(b, "sunken")
			self.app.setButtonFg(b, "black")
		
		# Launch thread in charge of receiving messages
		self.currentCall = C.Calls(self)
		if not self.secondLog:
			t = threading.Thread(target=self.currentCall.listenTCPConnections)
			t.daemon = True
			t.start()
		
		# Launch GUI
		self.app.go()

	# Función que gestiona los callbacks de los botones
	def buttonsCallback(self, button):

		if self.inCall and button not in ["Resume", "Pause", "Hang up"]:

			# The action cannot be realized since we are in a call
			self.errorLog("User tried to " + button + " but first he/she has to Hang up")
			return
		
		if not self.inCall and button in ["Resume", "Pause", "Hang up"]:

			# The action cannot be realized since we are NOT in a call
			self.errorLog("User tried to " + button + " but no call is running")
			return

		if button == "Quit":

			# Exit the app
			self.app.stop()
			return

		elif button == "Submit":

			# Start client with username and password received in input
			self.username = self.app.getEntry("Username")
			self.password = self.app.getEntry("Password ")
			
			# Now we try to connect to server
			try:
				self.initiateSocket()
			except socket.error:
				# Unable to initiate a socket
				self.errorLog("Please check your internet connection, your VPN, server field and server_dest_port field")
				self.app.stop()
				return

			# And try to register/update user's certificate
			try:
				message = "REGISTER {} {} {} {} V0".format(self.username, self.myIP, self.myReceiverPort, self.password)
				self.sock.send(bytes(message, 'utf-8'))
				response = self.sock.recv(1514).decode('utf-8')
			except:
				self.errorLog("Failed to send REGISTER message")
				self.sock.close()
				self.app.stop()
				return

			if response[0:2] != "OK":
				self.errorLog("Server response to REGISTER query is " + response)
				self.sock.close()
				self.app.stop()
				self.chooseLog(True, False)
				return

			self.sock.close()
			self.app.stop()
			self.startClient()
		
		elif button == "Refresh":

			# Refresh the list of registered users
			self.app.updateListBox("List", self.refreshListUsers(), select=False)
			return

		elif button == "Call":

			# Call the user selected in List
			self.currentCall.call()
			return

		elif button == "Resume":

			# Resume the call
			if self.inPause:
				self.currentCall.resume()
			else:
				self.errorLog("User tried to Resume but there is no call in Pause")
			return

		elif button == "Pause":

			# Pause the call
			if not self.inPause:
				if self.currentCall.pause():
					self.inPause = True
				else:
					self.app.setStatusbar("Failed to pause the call", 1)
			return

		elif button == "Hang up":

			# Hang up the call
			self.currentCall.hangup()
			return

		elif button == "Log out":

			# Reset username and password
			self.username = None
			self.password = None

			# Inform that when we log in again we keep using listenning socket
			self.secondLog = True

			# Stop client GUI
			self.app.stop()
			self.errorLog("Successfully logged out")

			# Start login window
			self.chooseLog(False, False)

		else:
			
			# The code should never reach this point
			self.app.stop()
			return
	
	# Print errors with timestamp
	def errorLog(self, error):
		t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		print('[{0}]:'.format(t), error)

	# We try to log using info contained in config.txt
	def logFromFile(self):
		values = {}
		# Open the file
		try:
			f = open(self.config, "r")
			f1 = f.readlines()
		except(FileNotFoundError):
			self.errorLog('Configuration file not found')
			raise FileNotFoundError
		
		# Parse the file
		try:
			for line in f1:
				(key, val) = line.split('=')
				if val[len(val)-1] == '\n':
					# Delete \n in case there is one at the end of the line
					val = val[:-1]
				values[key] = val
		except(ValueError):
			self.errorLog('Wrong syntax in configuration file must be: key=value')
			raise ValueError

		# Store the values
		try:
			self.username = values['username']
			self.password = values['password']
			if values['port'].isnumeric():
				self.myReceiverPort = int(values['port'])
			else:
				raise KeyError
		except(KeyError):
			self.errorLog('Key not found or port not Integer in configuration file')
			raise KeyError

		# Now we try to connect to server
		try:
			self.initiateSocket()
		except socket.error:
			# Unable to initiate a socket
			self.errorLog("Please check your internet connection, your VPN, server field and server_dest_port field")
			return

		# And try to register/update user's certificate
		try:
			message = "REGISTER {} {} {} {} {}".format(self.username, self.myIP, self.myReceiverPort, self.password, self.versions)
			self.sock.send(bytes(message, 'utf-8'))
			response = self.sock.recv(1514).decode('utf-8')
		except:
			self.errorLog("Failed to send REGISTER message")
			self.sock.close()
			raise socket.error

		if response[0:2] != "OK":
			self.errorLog("Server response to REGISTER query is " + response)
			self.sock.close()
			raise socket.error

		self.sock.close()

	def checkFile(self, button):
		# Check if the file exists and if the format is correct
		self.config = self.app.getEntry("File")
		self.app.stop()
		try:
			self.logFromFile()
			# If no error occured, start client
			self.startClient()

		except(FileNotFoundError, ValueError, KeyError):
			# Try again
			self.chooseLog(False, True)

		except socket.error:
			# Unable to initiate a socket
			self.errorLog("Please check your internet connection, your VPN, server field and server_dest_port field")

	def chooseLog(self, wrongPassword, wrongFile):
		self.app = gui("Login", "300x300")
		self.app.addLabel("LOG MANUALLY")
		self.app.setBg("lightgrey", override=True)
		self.app.setFg("black", override=True)
		self.app.entry("Username", label=True, focus=True)
		self.app.entry("Password ", label=True, secret=True)
		if wrongPassword:
			self.app.addLabel("PASSWORD WAS WRONG")
			self.app.setLabelFg("PASSWORD WAS WRONG", "red")
		self.app.buttons(["Submit", "Quit"], self.buttonsCallback)
		self.app.addLabel("LOG FROM FILE")
		self.app.entry("File", label=True, focus=True)
		self.app.setEntry("File", self.config, callFunction=False)
		if wrongFile:
			self.app.addLabel("FILE WAS WRONG")
			self.app.setLabelFg("FILE WAS WRONG", "red")
		self.app.buttons(["LOG IN"], self.checkFile)
		self.app.go()

	def __init__(self):
		self.chooseLog(False, False)

if __name__ == '__main__':

	vc = VideoClient()
	vc.stop()
	sys.exit() 