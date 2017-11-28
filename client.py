import socket
import sys
import threading
from chat_system import SystemOut
from chat_system import SystemIn

port = ''
if len(sys.argv)==1:
	print("No port specified,default is 12344")
	port=12345
else:
	port = int(sys.argv[1])
host = 'localhost'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:	#try to connect to server
	sock.connect((host,port))
except socket.error as msg:	#if we got error,close the socket and exit
	sock.close()
	print("Cannot connect to server")
	sys.exit(1)
if sock is not None:
	lock = threading.Lock()
	GateOut = SystemOut(sock)
	GateIn = SystemIn(sock, GateOut,lock)
	GateOut.start()
	GateIn.start()
	GateOut.join()
	GateIn.join()
	sock.close()
	sys.exit(1)