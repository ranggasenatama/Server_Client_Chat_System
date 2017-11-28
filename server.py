import socket
import sys
from connection import Connection
from user import User
import threading
host = 'localhost'
port = ''

if len(sys.argv) == 1:
	print("No port specified.Using default port 12345")
	port = 12345
else:
	port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(1)

threadID = 1
threads = [] #keep all the thread in a list
user = User() #user class is simple ORM for database user
user.loadUser()
lock = threading.Lock() #creating thread lock object to synchronize thread

while True: #handle all new incoming client
	try:
		conn, addr = sock.accept()
		connection = Connection(threadID,conn,addr,user,lock)
		threadID += 1
		connection.start()
		threads.append(connection)
	except KeyboardInterrupt: #stop receiving new connection with CTRL-C
		break

for t in threads: #wait all thread to finish running
	print("closing ",t.getName())
	t.join()

print("Exiting Program")