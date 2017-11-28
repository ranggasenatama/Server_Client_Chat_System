import sys
import threading

class SystemIn (threading.Thread):
	flag = 1
	def __init__(self,socket,SystemOut,lock):
		threading.Thread.__init__(self)
		self.socket = socket
		self.out = SystemOut
		self.lock = lock

	def run(self):
		flag = True
		self.receive()

	def __getMessage(self): #function to get full length of incoming data
		data = True
		buffer = bytearray()
		while data:
			data = self.socket.recv(2048)
			buffer.extend(data)
			if buffer.find(b'$$') != -1 : # the $$ is delimiter to tell the end of the command from user
				temp = buffer.decode()
				hasil = temp.split('$$')
				return hasil[0]

	def receive(self):
		while self.flag:
			incoming = self.__getMessage()
			if incoming == None:
				continue
			self.lock.acquire()
			message = incoming.split(" ",1)
			if message[0] == "+OK" :
				print("\nServer : OK! ",message[1])
			elif message[0] == "-ERR" :
				print("Server : Error! ",message[1])
			elif message[0] == "+MSG":
				message = message[1].split(" ",1)
				print(message[0]," : ",message[1])
			elif message[0] == "+EXIT" :
				self.flag = False
				self.out.stop()
				print("Closing connection")
			self.lock.release()

class SystemOut (threading.Thread):
	flag = 0
	def __init__(self,socket):
		threading.Thread.__init__(self)
		self.socket = socket

	def run(self):
		self.flag = True
		self.send()

	def stop(self):
		self.flag = False

	def send(self):
		while self.flag:
			message = input()
			message = message+"$$"
			self.socket.send(message.encode())
			print("Message Sent!")
