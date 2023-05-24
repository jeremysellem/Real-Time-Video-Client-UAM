from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import time, datetime
import socket, threading
import re, operator, ipaddress

clientsocket = None
clientPORT = None # Where the other user wants to receive data
clientIP = None
destNAME = None
sentOrder = 1
currentTimestamp = datetime.datetime.now()
n = 0

class Calls:

	# This functionality is not implemented yet but the funciton will be useful in the future
	def setImageResolution(self, resolution):
		# Se establece la resolución de captura de la webcam
		# Puede añadirse algún valor superior si la cámara lo permite
		# pero no modificar estos
		if resolution == "LOW":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160) 
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120) 
		elif resolution == "MEDIUM":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320) 
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) 
		elif resolution == "HIGH":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 

	def __init__(self, vc):
		self.client = vc
		self.app = vc.app
		self.subWindowLaunched = False

	def errorLog(self, error):
		t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		print('[{0}]:'.format(t), error)

	def showFrame(self, data):
		global currentTimestamp, n
		data = data.split(b"#",4)
		info = data[0:4]
		info[0] = info[0].decode('utf-8')
		info[1] = info[1].decode('utf-8')
		info[2] = info[2].decode('utf-8') # size
		info[3] = info[3].decode('utf-8')
		image = data[4]
		width = int(info[2].split('x')[0])
		height = int(info[2].split('x')[1])

		decimg = cv2.imdecode(np.frombuffer(image,np.uint8), 1)
		frame = cv2.resize(decimg, (width, height))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
		self.app.reloadImageData("Video", img_tk, fmt="jpg")
		n += 1
		delta = datetime.datetime.now() - currentTimestamp
		if delta.total_seconds() >= 1:
			# Afficher FPS dans la bar de statut
			currentTimestamp = datetime.datetime.now()
			self.app.setStatusbar("FPS = {0} Resolution = {1}".format(n, info[2]), 0)
			n = 0
		return

	def receiveUDPVideo(self):
		# Loop that receives and print UDP video packages
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((socket.gethostname(), self.client.myReceiverPort))
		sock.settimeout(5)
		self.errorLog("Start receiving UDP frames")
		while self.client.inCall and not self.client.inPause:
			try:
				data, addr = sock.recvfrom(15000)
				t = threading.Thread(target=self.showFrame, args=(data,))
				t.daemon = True
				t.start()
			except: 
				self.errorLog("Failed to receive from UDP socket")
		sock.close()
		self.errorLog("Stop receiving UDP frames")
		return
	
	def sendUDPVideo(self):
		global clientPORT, clientIP, sentOrder

		# Initiate UDP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Loop that sends UDP video packages from camera
		cap = cv2.VideoCapture(0)
		if not (cap.isOpened()):
			# Failed to open camera
			self.errorLog("Failed to open camera device, please check your webcam")
			sock.close()
			return
		
		self.errorLog("Start sending UDP frames")
		while self.client.inCall and not self.client.inPause:
			ret, frame = cap.read()
			if ret:
				data = cv2.resize(frame, (640,480)) #TODO: Here check a box menu with selected size
				ret, frame = cv2.imencode('.jpg', data, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
				if ret: 
					frame = frame.tobytes()
					package = "{}#{}#{}x{}#{}#".format(sentOrder, datetime.datetime.now(), 640, 480, 13) # FPS is fixed because I didn't understand how to use
					package = package.encode('utf-8')
					message = bytearray(package)
					message = message + frame
					try:
						sock.sendto(message, (clientIP, int(clientPORT)))
						sentOrder += 1
					except:
						self.errorLog("Failed to send frame, one image skipped")
				else:
					self.errorLog("Failed to encode camera image to jpg, one image skipped")
			else:
				self.errorLog("Failed to read from camera, one image skipped")

		self.errorLog("Stop sending UDP frames")
		sock.close()
		cap.release()
		return

	def handleNewConnection(self, cs, address):
		global clientsocket, clientPORT, clientIP, destNAME

		# If already in a call or receiving a call, send BUSY
		if self.subWindowLaunched:
			cs.send(bytes("CALL_BUSY "+self.client.username, 'utf-8'))
			cs.close()
			return

		clientIP = address[0]
		self.errorLog("A connection has been received from " + clientIP)
		
		message = cs.recv(1514).decode('utf-8')
		try:
			comando = message.split(' ')[0]
		except:
			self.errorLog("Message does not contain command")
			cs.close()
			return
		try:
			name = message.split(' ')[1]
			destNAME = name
		except:
			self.errorLog("Wrong syntaxis in: "+message)
			cs.close()
			return

		if comando == "CALLING" and not self.client.inCall:
			try:
				clientPORT = message.split(' ')[2]
			except:
				self.errorLog("Wrong syntaxis in: "+message)
				cs.close()
				return

			clientsocket = cs

			self.subWindowLaunched = True
			self.app.setStatusbar("Receiving a call from {0}...".format(name), 1)
			self.app.startSubWindow("CallDialogue", modal=True)
			self.app.setSize(200, 100)
			self.app.setBg("lightgrey", override=True)
			self.app.setFg("black", override=True)
			self.app.addLabel("Pregunta", "INCOMING CALL FROM\n")
			self.app.addLabel("Name", name)
			self.app.addButtons(["Accept", "Decline"], self.buttonsCallback)
			self.app.stopSubWindow()
			self.app.showSubWindow("CallDialogue")
			return

		elif comando == "CALL_END" and self.client.inCall:
			# End call
			self.app.setStatusbar("Received CALL_END from {0}".format(name), 1)
			self.errorLog("Received CALL_END")
			self.client.inCall = False
			self.app.setStatusbar("inCall = {}".format(self.client.inCall), 2)
			self.app.setStatusbar("FPS = 0 Resolution = 640x480", 0)
			self.app.setImage("Video", self.client.welcomePage)

		elif comando == "CALL_HOLD" and self.client.inCall:
			# Pause call
			if name == destNAME:
				self.app.setStatusbar("Received CALL_HOLD from {0}".format(name), 1)
				self.errorLog("Received CALL_HOLD from {0}".format(name))
				self.client.inPause = True

		elif comando == "CALL_RESUME" and self.client.inCall:
			# Resume call
			if name == destNAME:
				self.app.setStatusbar("Received CALL_RESUME from {0}".format(name), 1)
				self.errorLog("Received CALL_RESUME from {0}".format(name))
				self.client.inPause = False
				self.launchThreadsUDP()
		else:
			self.app.setStatusbar("Received {0} from {1}".format(comando, name), 1)
			self.errorLog("Received {0} from {1} but cannot handle it right now".format(comando, name))

		cs.close()
		return

	def sendTCPResponse(self, msg):
		global clientsocket
		try:
			clientsocket.send(bytes(msg, 'utf-8'))
			return True
		except:
			self.errorLog("Failed to send this message: "+msg)
			self.errorLog("At " + clientsocket.getpeername())
			return False

	def launchThreadsUDP(self):
		t1 = threading.Thread(target=self.receiveUDPVideo)
		t1.daemon = True
		t1.start()
		t2 = threading.Thread(target=self.sendUDPVideo)
		t2.daemon = True
		t2.start()
		return

	def buttonsCallback(self, button):
		global clientsocket

		if button == "Accept":
			if self.sendTCPResponse("CALL_ACCEPTED "+self.client.username+" "+str(self.client.myReceiverPort)):
				self.client.inCall = True
				self.app.setStatusbar("inCall = {}".format(self.client.inCall), 2)
				self.app.destroySubWindow("CallDialogue")
				self.subWindowLaunched = False
				self.app.setStatusbar("Call running with {}".format(destNAME), 1)

				# Launch a thread that sends UDP messages and one that receives and print images in GUI
				self.launchThreadsUDP()

			else:
				self.app.setStatusbar("User who called you ended socket connection", 1)
				self.app.destroySubWindow("CallDialogue")
				self.subWindowLaunched = False

		elif button == "Decline":
			self.sendTCPResponse("CALL_DENIED "+self.client.username)
			self.app.destroySubWindow("CallDialogue")
			self.subWindowLaunched = False

		else:
			self.errorLog("Unkown button pressed by user")

		clientsocket.close()
		return

	def listenTCPConnections(self):
		try:
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			address = (socket.gethostname(), self.client.myReceiverPort)
			server.bind(address)
			server.listen(5)
			threads = []
		except:
			self.errorLog("Unable to create a listenning socket, please restart application")
			return
		
		while True:
		    try:
		    	(clientsocket, address) = server.accept()
		    	# Launch thread in charge of parsing the message
		    	t = threading.Thread(target=self.handleNewConnection, args=(clientsocket,address))
		    	t.daemon = True
		    	threads.append(t)
		    	t.start()
		    except socket.error:
		    	self.errorLog("Closing receiving socket")
		    	break
		    except:
		    	self.errorLog("An unkown error occured while parsing a message")
	
	def call(self):
		global clientPORT, clientIP

		# Get username of user to call
		try:
			toCall = self.app.getListBox("List")[0]
			self.errorLog("User wants to call " + toCall)
		except:
			self.errorLog("User did not select any user in the list")
			return

		# Now we try to connect to server
		try:
			self.client.initiateSocket()
		except socket.error:
			# Unable to initiate a socket
			self.errorLog("Please check your internet connection, your VPN, server field and server_dest_port field")
			return
		
		# Send the QUERY query
		try:
			self.client.sock.send(bytes("QUERY {0}".format(toCall), 'utf-8'))
			response = self.client.sock.recv(1514).decode('utf-8')
		except:
			self.errorLog("Failed to send QUERY message")
			self.client.sock.close()
			return

		# Close socket with server, we don't need it anymore
		self.client.sock.close()

		# Parse response
		if response[0:2] != "OK":
			self.errorLog("Server response to QUERY query is " + response)
			return

		# Store target user info
		destIP = response.split(" ")[3]
		destPORT = response.split(" ")[4]
		protocols = sorted(response.split(" ")[5].split("#")) # Get available protocols as a sorted list
		self.errorLog("Successfully obtained his/her information")

		# Determine common best protocol
		myProtocols = sorted(self.client.versions.split("#"))
		myMaxProtocol = myProtocols[-1]
		while True:
			if myMaxProtocol in protocols:
				# The common protocol to be used is stored in myMaxProtocol
				self.errorLog("Max common protocol found: {0}".format(myMaxProtocol))
				break
			else:
				if myProtocols:
					# Update my max protocol by removing the last element
					myProtocols.pop()
					if myProtocols:
						myMaxProtocol = myProtocols[-1]
					else:
						# Did not find any protocol in common, not even V0
						self.errorLog("No common protocol found, cannot call this user")
						return	
				else:
					# Did not find any protocol in common, not even V0
					self.errorLog("No common protocol found, cannot call this user")
					return
		
		msg = "CALLING {} {}".format(self.client.username, self.client.myReceiverPort)
		self.app.setStatusbar("Calling {0} at {1}:{2}...".format(toCall, destIP, destPORT, myMaxProtocol), 1)

		infos = socket.getaddrinfo(destIP, destPORT)
		stream_info = [i for i in infos if i[1] == socket.SOCK_STREAM][0]
		s = socket.socket(*stream_info[:3])
		try:
			s.connect(stream_info[-1])
		except:
			self.errorLog("No response from {0} at {1}:{2}".format(toCall, destIP, destPORT))
			self.app.setStatusbar("{0} is not available".format(toCall), 1)
			return		
		s.send(bytes(msg, 'utf-8'))
		
		# The established sock is in s
		try:
			# 30 seconds timeout means the other user has 30s to answer
			s.settimeout(30)
			response = s.recv(1514)
		except:
			self.errorLog("Did not hear any answer from {0}".format(toCall))
			self.app.setStatusbar("{0} did not answer your call".format(toCall), 1)
			return

		try:
			comando = response.decode('utf-8').split(' ')[0]
		except:
			self.errorLog("Wrong syntaxis in response to CALLING")
			s.close()
			return

		if comando == "CALL_ACCEPTED":

			clientIP = destIP
			clientPORT = response.decode('utf-8').split(' ')[2]
			destNAME = toCall
			self.client.inCall = True
			self.app.setStatusbar("inCall = {}".format(self.client.inCall), 2)
			self.app.setStatusbar("Call running with {}".format(toCall), 1)
				
			# Launch a thread that sends UDP messages and one that receives and print images in GUI
			self.launchThreadsUDP()

		elif comando == "CALL_BUSY":
			self.app.setStatusbar("{0} is BUSY please call later".format(toCall), 1)
			
		elif comando == "CALL_DENIED":
			self.app.setStatusbar("{0} DENIED your call".format(toCall), 1)
			
		else:
			self.app.setStatusbar("{0} replied: {1} ".format(toCall, comando), 1)

		s.close()
		return

	def createTCPsocket(self):
		try:
			infos = socket.getaddrinfo(clientIP, clientPORT)
			stream_info = [i for i in infos if i[1] == socket.SOCK_STREAM][0]
			s = socket.socket(*stream_info[:3])
			s.connect(stream_info[-1])
			return s
		except:
			self.errorLog("Failed to create a TCP socket with {0}:{1}".format(clientIP, clientPORT))
			return False

	def resume(self):
		s = self.createTCPsocket()
		if not s:
			self.errorLog("Failed to send RESUME")
			return
		s.send(bytes("CALL_RESUME {0}".format(self.client.username), 'utf-8'))
		s.close()
		self.client.inPause = False
		self.launchThreadsUDP()
		self.app.setStatusbar("Sent CALL_RESUME to {0}".format(destNAME), 1)
		return True

	def pause(self):
		s = self.createTCPsocket()
		if not s:
			self.errorLog("Failed to send HOLD")
			return

		s.send(bytes("CALL_HOLD {0}".format(self.client.username), 'utf-8'))
		s.close()
		self.app.setStatusbar("Sent CALL_HOLD to {0}".format(destNAME), 1)
		return True

	def hangup(self):
		s = self.createTCPsocket()
		if not s:
			self.errorLog("Failed to send CALL_END to {0}".format(destNAME))
		else:
			s.send(bytes("CALL_END {0}".format(self.client.username), 'utf-8'))
			s.close()
			self.app.setStatusbar("Sent CALL_END to {0}".format(destNAME), 1)
		self.client.inCall = False
		self.app.setStatusbar("inCall = {}".format(self.client.inCall), 2)
		self.app.setStatusbar("FPS = 0 Resolution = 640x480", 0)
		self.app.setImage("Video", self.client.welcomePage)
		return


