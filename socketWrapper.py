import socket

class socketWrapper(socket.socket):
    
    def __getstate__(self):
        pass

    def __setstate(self, state):
        pass
    