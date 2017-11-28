import socket
import os
class User :
	online = {} #dictionary for online user
	def __init__(self):
		self.user = self.loadUser()

	def loadUser(self):
		dict = {}

		with open('userlist.txt','r') as file:
			for line in file : #add each line to dictionary
				if line == '\n':
					continue
				username, password =  line.split( )
				dict[username] = password
		file.close()
		return dict
	def getOnline(self): #get online user,return dictionary
		return self.online


	def auth(self,username,password,client): #auth function
		if username in self.user: #if username is exist
			if self.user[username] == password :
				self.online[username] = client
				return True, "+OK login success, welcome "+username+"$$"
			else :
				return False, "-ERR Wrong Password$$"
		else :
			return False, "-ERR Wrong Username$$"

	def register(self,username,password): #register new user
		if username in self.user: #return false if username is already exist
			return False,"-ERR Username Already exist$$"
		else :
			self.user[username] = password
			#add new user to online list
			file = open('userlist.txt','a')
			toWrite = username + ' ' + password + '\n'
			file.write(toWrite)
			file.close()
			return "+OK Register success, you can login now.$$"

	def logout(self,username):
		if username not in self.online:
			return
		else :
			del self.online[username]
			return "Exit Success$$"

