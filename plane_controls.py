#plane_controls.py

import logging
import serial
import serial.tools.list_ports
from relayUtils import *
from time import sleep
from abc import ABC, abstractmethod
from functools import partial
import socket

import inspect

class controller(ABC):
	"""A base controller class with no practical methods; should be overridden by your own class"""
	def __init__(self):
		super().__init__()

	@abstractmethod
	def com(self):
		"""Return a list of the commands that this controller can take"""

		"""
		Returns: A dictionary with the keys being the commands this controller can take. 
		The values of this dictionary will, of necessity, be implementation specific
		"""
		pass
	
	@abstractmethod
	def sendCommand(self, command, state):
		"""Send the commands which control the automation"""

		"""
		Command(str): The name of the command to send
		State(str): The state of the command to send, e.g. "Activate", "Cancel", etc.
		These might be more accurately called "Axis" and "State command"...
		Returns: None

		"""
		pass

class SerialPlaneController(controller):

	#The keys are the original memory address of the command in the DOS program
	#The values are the serial values to output, and should be terminated with an 'Od' character
	serialTable = {
		'F200': '>01AA2', 			#Power on Reset 1
		'F210': '>02AA3',			#				2
		'F220': '>03AA4',			#				3
		'F230': '>04AA4',			#				4
		'F240': '>01BA3',			# Reset			1		
		'F250': '>02BA4',			#				2
		'F260': '>03BA5',			#				3				
		'F270': '>04BA6',			#				4
		'F280': '>01IFFFFC2',		# Set all as outputs 	1
		'F290': '>02IFFFFC3',		#						2
		'F2A0': '>03IFFFFC4',		#						3	
		'F2B0': '>04HFFFFC4',		#						4
		'F2C0': '>04MB1',			# Read digital i/o
		'F2D0': '>01K00016D',
		'F2E0': '>01L00016E',
		'F2F0': '>01K00026E',
		'F300': '>01L00026F',
		'F310': '>01K000470',
		'F320': '>01L000471',
		'F330': '>01K000874',
		'F340': '>01L000875',
		'F350': '>01K00106D',
		'F360': '>01L00106E',
		'F370': '>01K00206E',
		'F380': '>01L00206F',
		'F390': '>01K004070',
		'F3A0': '>01L004071',
		'F3B0': '>01K008074',
		'F3C0': '>01L008075',
		'F3D0': '>01K01006D',
		'F3E0': '>01L01006E',
		'F3F0': '>01K02006E',
		'F400': '>01L02006F',
		'F410': '>01K040070',
		'F420': '>01L040071',
		'F430': '>01K080074',		# Main gear door close
		'F440': '>01L080075',		# Deactivate Digital Output # ???? of 1
		'F450': '>01K10006D',
		'F460': '>01L10006E',
		'F470': '>01K20006E',
		'F480': '>01L20006F',
		'F490': '>01K400070',
		'F4A0': '>01L400071',
		'F4B0': '>01K800074',
		'F4C0': '>01L800075',
		'F4D0': '>02K00016E',		#Activate digital output # ??? of 2 - main gear up (panel 1 # 16)
		'F4E0': '>02L00016F',		#Deactive digtal output # ??? of 2 - main gear up cancel
		'F4F0': '>02K00026F',
		'F500': '>02L000270',
		'F510': '>02K000471',		# Activate Digital output # ???? of 2 - Nose Gear Up (panel 1 # 18)
		'F520': '>02L000472',		# Deactive digtial output # ??? of 2 - Nose gear up cancel
		'F530': '>02K000875',
		'F540': '>02L000876',
		'F550': '>02K00106E',		# Activate digital output # ??? of 2 - Inboard Flap Up (grayhill 1 # 20)
		'F560': '>02L00106F',		#Deactivate digital output # ??? of 2 - inboard flap up cancel
		'F570': '>02K00206F',
		'F580': '>02L002070',
		'F590': '>02K004071',		#Activate digital output # ??? of 2 - Outboard flap up (grayhill 1 # 22)
		'F5A0': '>02L004072',		#Deactiveate digital output # ??? of 2 - outboard flap up cancel
		'F5B0': '>02K008075',
		'F5C0': '>02L008076',
		'F5D0': '>03K00016F',
		'F5E0': '>03L000170',
		'F5F0': '>03K000270',
		'F600': '>03L000271',
		'F610': '>03K000472',
		'F620': '>03L000473',
		'F630': '>03K000876',
		'F640': '>03L000877',
		'F650': '>03K00106F',
		'F660': '>03L001070',
		'F670': '>03K002070',
		'F680': '>03L002071',
		'F690': '>03K004072',
		'F6A0': '>03L004073',
		'F6B0': '>03K008076',
		'F6C0': '>03L008077',
		'F6D0': '>03K01006F',
		'F6E0': '>03L010070',
		'F6F0': '>03K020070',
		'F700': '>03L020071',
		'F710': '>03K040072',
		'F720': '>03L040073',
		'F730': '>03K080076',
		'F740': '>03L080077',
		'F750': '>03K10006F',
		'F760': '>03L100070',
		'F770': '>03K200070',
		'F780': '>03L200071',
		'F790': '>03K400072',
		'F7A0': '>03L400073',
		'F7B0': '>03i800014FF85',
		'F7C0': '>03i8000000054',
	}

	def com(self):
		return self.commands

	#This is the list of serial commands listed in the original dos program under
	#"INIT THE PLANE", per Bill Hogan's notes
	#The D instruction stands for Delay Microseconds
	initList = (['F200','F210', 'F220','F230','F240','F250','F260', 'F270',
				'F280','F290', 'F2A0','F2B0','F440','F510','F4D0', 'F550',
				'F590', 'F340', 'F410'],
				['F520','F4E0','F560','F5A0','F430', 'F270', 'F420']
				)


	def __init__(self, name=None, dummy=False):
		logging.info("Initializing controller object")
		if name != None:
			logging.info(f"Attempting to open Serial port with given name {name}")
			self.ser =  serial.Serial(port = name, baudrate=9600, timeout=3, rtscts=False, dsrdtr=False)
			logging.info(f"Opened com port {self.ser.port}")
		else:
			self.ser = serial.Serial(port=None, baudrate=9600, timeout=3, rtscts=False, dsrdtr=False)
		
		ports = serial.tools.list_ports.comports()

		for p in ports:
			logging.debug(f"Available serial port : {p.device}")

		if self.ser.port == None:
			if dummy == True:
				logging.warning("Serial device initialized as dummy")
				self.ser.port = None
			elif len(ports) == 1:
				self.ser.port=ports[0].device
				try:
					self.ser.open()
					logging.info(f"Opened com port {self.ser.port}")
				except serial.SerialException as e:
					logging.warning("Could not open serial output port\n", e)
					self.ser.port = None
			elif len(ports) > 0:
				#TODO: Dialogue to choose which Comm port to open if there are multiple ports
				self.ser.port=ports[0].device
				self.ser.open()
				logging.info(f"Opened com port {self.ser.port}")
			else: 
				logging.warning("Found no serial ports to open")
				self.ser = None
		logging.debug(f"Full serial info for serial output device: {self.ser}")

		self.commands = {
			'nose gear down'		:	{'activate':partial(self.sendDOSCommand, 'F530'),'cancel':partial(self.sendDOSCommand, 'F540')},
			'nose gear up'			:	{'activate':partial(self.sendDOSCommand, 'F510'),'cancel':partial(self.sendDOSCommand, 'F520')},
			'main gear down'		:	{'activate':partial(self.sendDOSCommand, 'F4F0'),'cancel':partial(self.sendDOSCommand, 'F500')},
			'main gear up'			:	{'activate':partial(self.sendDOSCommand, 'F4D0'),'cancel':partial(self.sendDOSCommand, 'F4E0')},
			'inboard flap up'		:	{'activate':partial(self.sendDOSCommand, 'F550'),'cancel':partial(self.sendDOSCommand, 'F560')},
			'inboard flap down'		:	{'activate':partial(self.sendDOSCommand, 'F570'),'cancel':partial(self.sendDOSCommand, 'F580')},
			'outboard flap up'		:	{'activate':partial(self.sendDOSCommand, 'F590'),'cancel':partial(self.sendDOSCommand, 'F5A0')},
			'outboard flap down'	:	{'activate':partial(self.sendDOSCommand, 'F5B0'),'cancel':partial(self.sendDOSCommand, 'F5C0')},
			'elevator up'			:	{'activate':partial(self.sendDOSCommand, 'F2D0'),'cancel':partial(self.sendDOSCommand, 'F2E0')},
			'rudder left'			:	{'activate':partial(self.sendDOSCommand, 'F2F0'),'cancel':partial(self.sendDOSCommand, 'F300')},
			'rudder right'			:	{'activate':partial(self.sendDOSCommand, 'F310'),'cancel':partial(self.sendDOSCommand, 'F320')},
			'thrust reverser open'	:	{'activate':partial(self.sendDOSCommand, 'F330'),'cancel':partial(self.sendDOSCommand, 'F340')},
			'thrust reverser close' :	{'activate':partial(self.sendDOSCommand, 'F410'),'cancel':partial(self.sendDOSCommand, 'F420')},
			'ground spoiler'		:	{'activate':partial(self.sendDOSCommand, 'F350'),'cancel':partial(self.sendDOSCommand, 'F360')},
			'leading edge slats'	:	{'activate':partial(self.sendDOSCommand, 'F370'),'cancel':partial(self.sendDOSCommand, 'F380')},
			'kruger flaps'			:	{'activate':partial(self.sendDOSCommand, 'F390'),'cancel':partial(self.sendDOSCommand, 'F3A0')},
			'flight spoilers'		:	{'activate':partial(self.sendDOSCommand, 'F3B0'),'cancel':partial(self.sendDOSCommand, 'F3C0')},
			'inboard aileron down'	:	{'activate':partial(self.sendDOSCommand, 'F3D0'),'cancel':partial(self.sendDOSCommand, 'F3E0')},
			'inboard aileron up'	:	{'activate':partial(self.sendDOSCommand, 'F3F0'),'cancel':partial(self.sendDOSCommand, 'F400')},
			'main gear door close'	:	{'activate':partial(self.sendDOSCommand, 'F430'),'cancel':partial(self.sendDOSCommand, 'F440')},
			'outboard aileron down'	:	{'activate':partial(self.sendDOSCommand, 'F450'),'cancel':partial(self.sendDOSCommand, 'F460')},
			
			'outboard aileron up'	:	{'activate':partial(self.sendDOSCommand, 'F470'),'cancel':partial(self.sendDOSCommand, 'F480')},
			'wing tail nav lights'	:	{'activate':partial(self.sendDOSCommand, 'F5D0'),'cancel':partial(self.sendDOSCommand, 'F5E0')},
			'landing lights'		:	{'activate':partial(self.sendDOSCommand, 'F5F0'),'cancel':partial(self.sendDOSCommand, 'F600')},
			'rotating beacons'		:	{'activate':partial(self.sendDOSCommand, 'F630'),'cancel':partial(self.sendDOSCommand, 'F640')},
			'turnoff light'			:	{'activate':partial(self.sendDOSCommand, 'F690'),'cancel':partial(self.sendDOSCommand, 'F6A0')},
			'wing illumination light':	{'activate':partial(self.sendDOSCommand, 'F6B0'),'cancel':partial(self.sendDOSCommand, 'F6C0')},
			'nose wheel taxi light'	:	{'activate':partial(self.sendDOSCommand, 'F6D0'),'cancel':partial(self.sendDOSCommand, 'F6E0')},
			'tinkerbell'			:	{'activate':partial(self.sendDOSCommand, 'F7B0'),'cancel':partial(self.sendDOSCommand, 'F7C0')},
			'init the plane'		: 	{'activate':partial(self.initThePlane)},
			'reset plane controller':	{'activate':partial(self.resetPlaneController)}
		}

	def close(self):
		self.ser.close()

	def getPort(self):
		return str(self.ser.port)

	def sendCommand(self, command, state):
		logging.info("Preparing to send command " + str(command) + ":"+str(state))
		if command not in self.commands:
			raise ValueError('No command identified by string ' + str(command))
		elif state not in ['activate','cancel']:
			raise ValueError("State must be either activate or cancel for all commands; was given " + str(state))
		elif self.ser == None:
			raise OSError("No serial port could be found on this computer")
		elif not self.ser.isOpen():
			raise OSError(f"Serial port {str(self.ser)} is not open")
		else:
			self.commands[command][state]()
			#c = SerialPlaneController.serialTable[self.commands[command][state]]
			#self.ser.write((c + '\r').encode())
			logging.info(f"Sent command with data {command} {state}")

	def sendDOSCommand(self, dosCommand):
		c = SerialPlaneController.serialTable[dosCommand]
		if self.ser.is_open:
			try:
				self.ser.write((c + '\r').encode())
				#self.ser.write((c).encode())
				logging.info(f"Sent command with DOS label {dosCommand} and data {c}")	
			except serial.serialutil.SerialException as e:
				raise(e)
		else:
			curframe = inspect.currentframe()
			calframe = inspect.getouterframes(curframe, 2)
			#print('caller name:', calframe[1][3])
			logging.warning(f"Wanted to send command with DOS label {dosCommand} and data {c} but serial port is not open")
			logging.warning(f"Serial port info is: {self.ser}")

	def sendRawCommand(self, command):
		logging.debug(f"Preparing to send raw command with string {command}")
		if self.ser.is_open:
			try:
				self.ser.write((command + '\r').encode())
				#self.ser.write((command + '\r').encode())
				logging.debug(f"Raw command sent with data {command}")
			except serial.serialutil.SerialExeption as err:
				raise(f"Error sending raw command: {err}")
		else:
			logging.debug("Serial port not open")

	def initThePlane(self):
		logging.info("Initializing the plane")
		for i in self.initList[0]:
			self.sendDOSCommand(i)
			sleep(.1)
		sleep(35)
		for i in self.initList[1]:
			self.sendDOSCommand(i)
			sleep(.1)
		logging.info("Completed initializing the plane")

	def resetPlaneController(self):
		logging.info("Resetting plane controller")
		for i in self.initList[0][:12]:
			self.sendDOSCommand(i)
			sleep(.1)

class RelayLightingController(controller):

	def __init__(self):

		self.relays = relayBoard()
		try:
			self.relays.loadLib()
			ids = self.relays.enumDevs()
			if len(ids) > 0:
				self.relays.openDevById(ids[0])
		except:
			logging.warning("No relay board opened")

		self.commands = {
			'On'					:	{'open':partial(self.relays.openRelay, 1), 'close':partial(self.relays.closeRelay, 1), 'blink':partial(self.relays.blinkRelay, 1)},
			'Nite'					:	{'open':partial(self.relays.openRelay, 2), 'close':partial(self.relays.closeRelay, 2), 'blink':partial(self.relays.blinkRelay, 2)},
			'Preset 3'				:	{'open':partial(self.relays.openRelay, 3), 'close':partial(self.relays.closeRelay, 3), 'blink':partial(self.relays.blinkRelay, 3)},
			'Evt2 Nite/Planes'		:	{'open':partial(self.relays.openRelay, 4), 'close':partial(self.relays.closeRelay, 4), 'blink':partial(self.relays.blinkRelay, 4)},
			'Evt3 Nite/No Planes'	:	{'open':partial(self.relays.openRelay, 5), 'close':partial(self.relays.closeRelay, 5), 'blink':partial(self.relays.blinkRelay, 5)},
			'Dusk'					:	{'open':partial(self.relays.openRelay, 6), 'close':partial(self.relays.closeRelay, 6), 'blink':partial(self.relays.blinkRelay, 6)},
			'Preset 7'				:	{'open':partial(self.relays.openRelay, 7), 'close':partial(self.relays.closeRelay, 7), 'blink':partial(self.relays.blinkRelay, 7)},
			'Off'					:	{'open':partial(self.relays.openRelay, 8), 'close':partial(self.relays.closeRelay, 8), 'blink':partial(self.relays.blinkRelay, 8)},
			'all' 					: {'open':self.relays.openAllRelays, 'close':self.relays.closeAllRelays}
		}

	def com(self):
		return self.commands

	def sendCommand(self, command, state):
		logging.info(f"Lighting controller preparing to send command {command}")
		if command not in self.commands:
			raise ValueError(f"No command identified by string {command}")
		elif state not in self.commands[command]:
			raise ValueError(f"State for command {command} must be one of {self.commands[command]}")
		elif self.relays == None:
			raise OSError("No relay board is active or connected")
		else:
			return self.commands[command][state]

class NetworkLightingController(controller):

	#A copy/pase of the CueScript strings stored in the Cueserver
	buttonStringsFromCS = [
		[b""],
		[b"Playback 1 Cue 14 Go;", b"Playback 2 Cue 6 Go;", b"Wait 6 Cue 6.1 Fade 10 Go;", b" Playback 3 Cue 9 Go;", b"Playback 4 Cue 12 Go;", b"Button 1 > 8 Off;", b"Button 1 On;"],
		[b"Playback 1 Cue 14 Go;", b"Playback 2 Cue 7 Go;", b"Wait 6 Cue 7.1 Fade 10 Go;", b" Playback 3 Cue 10 Go;", b"Playback 4 Cue 12 Go;", b"Button 1 > 8 Off;", b"Button 2 On;"],
		[b"Playback 1 Cue 16 Go;", b"Button 3 On"],
		[b"Playback 1 Cue 17 Go;", b"Button 1 > 8 Off;", b"Button 4 On"],
		[b"Playback 1 Cue 18 Go;", b"Button 1 > 8 Off;", b"Button 5 On"],
		[b"Playback 1 Cue 14 Go;", b"Playback 2 Cue 6 Go;", b"Playback 3 Cue 9 Go;", b"Playback 4 Cue 12 Go;", b"Button 1 > 8 Off;", "Button 6 On;"],
		[b"Contact 2 Disable;", b"Playback 1 Cue 2 Go;", b"Button 1 > 8 Off;", b"Button 2 At 6;", b"Wait 120;", b"Cue 1 Go;", b"Button 2 Off;", b"Button 1 On;", b"Contact 2 Enable"],
		[b"Playback 1 Release;", b"Playback 2 Release;", b"Playback 3 Release;", b"Playback 4 Release;", b"Button 1 > 8 Off;", b"Button 8 On"]
	]

	#A copy/paste of the commands triggered by the contact closures on the Cueserver
	contactStringsFromCS = [
		[b""],
		[b"\"TIMER\" = 0;", b"Playback 1 Cue 14 Go;", b"Playback 2 Cue 6 Fade 14 Go;", b"Playback 4 Cue 12 Go;", b"Playback 2 Wait 16 Cue 6.1 Fade 10 Go;", b"Playback 3 Cue 9 Go;", b"Button 8 Off;", b"Button 1 On;"],
		[b"\"TIMER\" = 0;", b"Playback 1 Cue 14 Go;", b"Playback 2 Cue 6 Fade 14 Go;", b"Playback 3 Cue 10 Go;", b"Playback 4 Cue 12 Go;", b"Playback 2 Wait 16 Cue 7.1 Fade 10 Go;", b"Button 1 > 8 Off;", b"Button 2 On;"],
		[b"Playback 1 Cue 20 Go;", b"Button 3 At 4;", b"\"TIMER\" = 1;", b"Wait 3600;", b"IF {{TIMER}} THEN;", b"Playback 1 Release;", b"Button 3 Off;", b"\"TIMER\" = 0",],
		[b"\"TIMER\" = 0;", b"Playback 1 Cue 17 Go;", b"Button 1 > 8 Off;", b"Button 4 On;"],
		[b"\"TIMER\" = 0;", b"Playback 1 Cue 18 Go;", b"Button 1 > 8 Off;", b"Button 5 On;"],
		[b"\"TIMER\" = 0;",  b"Playback 1 Cue 14 Go;", b"Playback 2 Cue 6 Go;", b"Playback 3 Cue 11 Go;", b"Playback 4 Cue 12 Go;", b"Button 1 > 8 Off;", b"Button 6 On;"],
		[b"\"TIMER\" = 0;", b"Cue 16 Go;", b"Button 3 On;"],
		[b"\"TIMER\" = 0;", b"Playback 1 Release;", b"Playback 2 Release;", b"Playback 3 Release;", b"Playback 4 Release;", b"Button 1 > 8 Off;", b"Button 8 On"]
	]

	def __init__(self, ip = "10.101.10.205", port = 52737):
		self.ip = ip
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.commands = {
			'CC1:Main Look'				:	{'press':partial(self.sendCSContactClosure, 1)},
			'CC2:Night'					:	{'press':partial(self.sendCSContactClosure, 2)},
			'CC3:Cleaning'				:	{'press':partial(self.sendCSContactClosure, 3)},
			'CC4:Event2 Low w-Planes'	:	{'press':partial(self.sendCSContactClosure, 4)},
			'CC5:Event2 Low w-o-Planes'	:	{'press':partial(self.sendCSContactClosure, 5)},
			'CC6:Sunrise-Sunset Only'	:	{'press':partial(self.sendCSContactClosure, 6)},
			'CC7:Event 1 Medium Day'	:	{'press':partial(self.sendCSContactClosure, 7)},
			'CC8:Off'					:	{'press':partial(self.sendCSContactClosure, 8)},
			'B1:Main On-Day'			:	{'press':partial(self.sendCSButtonPress, 1)},
			'B2:Night'					:	{'press':partial(self.sendCSButtonPress, 2)},
			'B3:Event 1 Medium'			:	{'press':partial(self.sendCSButtonPress, 3)},
			'B4:Event 2 w-Planes'		:	{'press':partial(self.sendCSButtonPress, 4)},
			'B5:Event 2 w-o-Planes'		:	{'press':partial(self.sendCSButtonPress, 5)},
			'B6: Sunrise-Sunset ONly'	:	{'press':partial(self.sendCSButtonPress, 6)},
			'B7:2 Minute Surprise'		:	{'press':partial(self.sendCSButtonPress, 7)},
			'B8:Off'					:	{'press':partial(self.sendCSButtonPress, 8)},
		}



	def com(self):
		return self.commands

	def sendCommand(self, command, state):
		logging.info(f"Network Lighting controller preparing to send command {command}")
		if command not in self.commands:
			raise ValueError(f"No command identified by string {command}")
		elif state not in self.commands[command]:
			raise ValueError(f"State for command {command} must be one of {self.commands[command]}")
		else:
			return self.commands[command][state]

	def sendRawMessage(self, message):
		logging.debug(f"Sending UDP command with target IP {self.ip} and port {self.port} and message {message}")
		self.sock.sendto(message, (self.ip, self.port))

	def sendCSButtonPress(self,buttonNum):
		for command in NetworkLightingController.buttonStringsFromCS[buttonNum]:
			self.sendRawMessage(command)

	def sendCSContactClosure(self, contactNum):
		for command in NetworkLightingController.contactStringsFromCS[contactNum]:
			self.sendRawMessage(command)

	def __getstate__(self):
		myDict = self.__dict__
		myDict['sock'] = None
		return myDict

	def __setstate__(self, state):
		self.__dict__ = state
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	controller = SerialPlaneController('COM3')

	if (False):
		controller.sendCommand('reset plane controller', 'activate')
		exit()

	sleep(10)

	controller.sendCommand("thrust reverser open", "activate")
	sleep(1)
	controller.sendCommand("thrust reverser open", "cancel")
	sleep(1)

	controller.sendCommand('thrust reverser close', 'activate')
	sleep(1)
	controller.sendCommand('thrust reverser close', 'cancel')

	#con = NetworkLightingController()
	#con.sendCSContactClosure(1)
