#https://github.com/andymccurdy/redis-py
#https://github.com/bakwc/PySyncObj
#https://realpython.com/intro-to-python-threading/#what-is-a-thread
#https://redislabs.com/ebook/appendix-a/a-3-installing-on-windows/a-3-2-installing-redis-on-window/

import redis
import pysyncobj
import threading
import sys
from pysyncobj import SyncObj, replicated

'''
holds a history of all commands applied to redis
replicated over all nodes so all nodes can apply 
same command to local redis
'''
class Raft(SyncObj):
	def __init__(self, selfNodeAddr, otherNodeAddrs):
		super(Raft, self).__init__(selfNodeAddr, otherNodeAddrs)
		self.__history = []
		
	def getIndex(self):
		return len(self.__history)
	
	#remove this later
	def getHistory(self):
		return self.__history
	
	@replicated
	def addRedis(self, command):
		self.__history.append(command)
		return self.__history

#if there is an unapplied command, apply it
def updateRedis(red, raft):
	localCount = 0
	while(True):
		if localCount < raft.getIndex():
			processCommand(red, raft.getHistory()[localCount])
			localCount+= 1

#process a command, might want to make this better
def processCommand(red, command):
	if command["command"] == "set":
		red.set(command["key"], command["value"])
	else:
		print("oops")

#gets stuff from command line, and responds apropriately
def commandLineOperation(r, raft):
	toRedis = {}
	while(True):
		command = input(">> ")
		#display a value
		if command == "get":
			commandGet = input("get>> ")
			print(r.get(commandGet))
		#modify local database without going
		#through raft, take this out once 
		#testing is done
		elif command == "force":
			commandSet = input("set>> ")
			commandSetTo = input("set:to>> ")
			print(r.set(commandSet, commandSetTo))
		#set a key value pair though raft
		elif command == "set":
			toRedis["command"] = "set"
			toRedis["key"] = input("set>> ")
			toRedis["value"] = input("set:to>> ")
			raft.addRedis(toRedis)
		#get some back end info
		elif command == "info":
			print(raft.isReady())
			print(raft.getHistory())
		else:
			print("oops")

if len(sys.argv) < 3:
	print('Usage: %s self_port partner1_ip partner1_port ...' % sys.argv[0])
	sys.exit(-1)
#connect to local redis
red = redis.Redis(host='localhost', port=6379, db=0)

#set up raft for communication
#TODO:Make it work with more than one partner
port = "localhost:%d" % int(sys.argv[1])
partner = ["%s:%d" % (sys.argv[2], int(sys.argv[3]))]
print(port)
print(partner)
raft = Raft(port, partner) 

#watch raft to see if another node has updated
update = threading.Thread(target=updateRedis, args=(red, raft, ), daemon=True)
update.start()

#start getting redis operations from the command line
commandLineOperation(red, raft)