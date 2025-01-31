import socket

UDP_IP = "10.0.1.101"
UDP_PORT = 52737
#MESSAGE = b"Hello, World!"
MESSAGE = b"BUTTON 1 OFF"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))