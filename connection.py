import socket
import sys
import threading
from Crypto.Cipher import AES 
from Crypto import Random 

class Connection (threading.Thread):
	IV = Random.new().read(16)
	auth = False #the authentication state of connection
	username = ''
	_flag = True
	def __init__(self,threadID,client,addr,user,lock):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = addr
		self.client = client #sock connection
		self.user = user #instance from user class
		self.lock = lock

	def run(self):
		print("New connection started")
		print("Connected to ",self.name)
		#run mainLoop when thread start
		self.mainLoop()

	def stop(self):
		print("Closing",self.name,"connection")
		if self.auth == True:
			message = self.user.logout(self.username)
			message = '+EXIT ' + message + '$$'
		else :
			message = '+EXIT Closing Connection to Client$$'
		self._flag = False
		return message


	def __getMessage(self): #function to get full length of incoming data
		data = True
		buffer = bytearray()
		while data:
			data = self.client.recv(2048)
			buffer.extend(data)
			if buffer.find(b'$$') != -1 : # the $$ is delimiter to tell the end of the command from user
				temp = buffer.decode()
				hasil = temp.split('$$')
				return hasil[0]

	def chat(self,target,message):
		#check if chat target is on the online list
		onlineUser = self.user.getOnline()
		send_string = "+MSG "+self.username+" "+message+"$$"
		try :
			send_sock = onlineUser[target]
		except KeyError:
			message = "-ERR "+ target + " Offline$$"
			return message

		#send to specific address
		send_sock.send(send_string.encode())
		return '+OK Message to '+target+' sent$$'

	def online(self): #get online user list
		onlineUser = self.user.getOnline()
		onlineUser = onlineUser.keys()
		#change list to string
		message = "+OK "+ ' '.join(onlineUser) + "$$"
		return message

	def broadcast(self,message):
		#for each socket in the socket list dictionary
		onlineUser = self.user.getOnline()
		message = '+MSG ' +self.username+ ' ' + message + '$$'
		for socket in onlineUser:
			onlineUser[socket].send(message.encode())
		return "+OK Message broadcasted$$"

	def encryption_CHAT(self,target,message):
		c = AES.new('abcd1234efgh5678', AES.MODE_CFB, self.IV)
		data = message.encode('utf-8')
		data = c.encrypt(data) #  2
		data2 = data
		# print ("{} ".format(data))
		c = AES.new('abcd1234efgh5678', AES.MODE_CFB, self.IV) 
		data = c.decrypt(data) # 1
		data = data.decode('utf-8') # 2
		onlineUser = self.user.getOnline()
		send_string = "+MSG "+self.username+" " + data + "$$"
		try :
			send_sock = onlineUser[target]
		except KeyError:
			data = "-ERR "+ target + " Offline$$"
			print ("{} ".format(data))
			return ''
		#send to specific address
		send_sock.send(send_string.encode())
		print ("+OK Encrypted Message {} to {} sent$$".format(data2,target))
		return ''

	def encryption_BC(self,message):
		c = AES.new('abcd1234efgh5678', AES.MODE_CFB, self.IV)
		data = message.encode('utf-8')
		data = c.encrypt(data) #  2
		data2 = data
		# print ("{} ".format(data))
		c = AES.new('abcd1234efgh5678', AES.MODE_CFB, self.IV) 
		data = c.decrypt(data) # 1
		data = data.decode('utf-8') # 2
		#for each socket in the socket list dictionary
		onlineUser = self.user.getOnline()
		message = '+MSG ' +self.username+ ' ' + data + '$$'
		for socket in onlineUser:
			onlineUser[socket].send(message.encode())
		print ("+OK Encrypted Broadcast Message {} sent$$".format(data2))
		return ''

	def mainLoop(self):
		while self._flag:
			command = self.__getMessage()
			#incoming command argument is seperated with _
			if command == None :
				continue
			print("INCOMING : ",command)
			command = command.split('_')
			#split so we can read the command easily

			#system object include the standart function and the online userdata

			#command with a no argument can be accessed without authentication
			if len(command) == 1:
				if command[0] == 'QUIT':
					#Quit command will close the connection and stop the thread
					message = self.stop()
					self.client.send(message.encode())
					self.client.close()
					break
				elif command[0] == 'ONLINE':
					message = self.online()
					self.client.send(message.encode())
				else :
					self.client.send(b'Wrong Command$$')
			elif len(command) == 2:
				if command[0] == 'BC' and self.auth == True:
					#broadcast function call
					message = self.broadcast(command[1])
					self.client.send(message.encode())
				else :
					self.client.send(b'Wrong Command or you\'re not Authenticated$$')
			#chat can only be run by a authenticated user
			elif len(command) == 3:
				if command[0] == 'LOGIN':
				#login set the auth state to true
					self.lock.acquire() #lock the shared open file
					self.auth, message = self.user.auth(command[1],command[2],self.client)
					self.lock.release() #release the lock
					self.username = command[1]
					self.client.send(message.encode())
				elif command[0] == 'REGISTER':
				#register add a new user to database and loggin it in after successful register
					self.lock.acquire()  # lock the shared open file
					message = self.user.register(command[1],command[2])
					self.lock.release()  # release the lock
					self.client.send(message.encode())
				elif command[0] == 'CHAT' and self.auth == True:
					message = self.chat(command[1],command[2])
					self.client.send(message.encode())
				elif command[0] == 'ENCRYP' and command[1] == 'BC' and self.auth == True:
					message = self.encryption_BC(command[2])
				else :
					self.client.send(b'Wrong Command or you\'re not Authenticated$$')
			elif len(command) == 4:
				if command[0] == 'ENCRYP' and command[1] == 'CHAT' and self.auth == True:
					# print ("testing")
					message = self.encryption_CHAT(command[2],command[3])
				else :
					self.client.send(b'Wrong Command or you\'re not Authenticated$$')
