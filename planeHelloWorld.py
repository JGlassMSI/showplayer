from plane_controls import *
import logging
from time import sleep

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	con = SerialPlaneController("COM7")
	print(con.ser)
	sleep(30)
	#con.initThePlane()
	con.sendCommand('thrust reverser', 'activate')
	sleep(5)
	con.sendCommand('thrust reverser', 'cancel')
	print(con.ser.read())
	con.close()
	print("End of program")