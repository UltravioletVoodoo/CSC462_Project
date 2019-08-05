#https://github.com/andymccurdy/redis-py
#https://github.com/bakwc/PySyncObj
#https://realpython.com/intro-to-python-threading/#what-is-a-thread
#https://redislabs.com/ebook/appendix-a/a-3-installing-on-windows/a-3-2-installing-redis-on-window/

import redis
import pysyncobj
import threading
import sys
from pysyncobj import SyncObj, replicated

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

def updateRedis(red, raft):
	localCount = 0
	while(True):
		if localCount < raft.getIndex():
			processCommand(red, raft.getHistory()[localCount])
			localCount+= 1

def processCommand(red, command):
	if command["command"] == "set":
		red.set(command["key"], command["value"])
	else:
		print("oops")

def redisOperation(r, raft):
	while(True):
		command = input(">> ")
		if command == "get":
			commandGet = input("get>> ")
			print(r.get(commandGet))
		elif command == "set":
			commandSet = input("set>> ")
			commandSetTo = input("set:to>> ")
			print(r.set(commandSet, commandSetTo))
		elif command == "test":
			testy = {}
			testy["command"] = "set"
			testy["key"] = "foo"
			testy["value"] = "bar"
			raft.addRedis(testy)
			print(raft.getHistory())
		elif command == "info":
			print(raft.isReady())
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
redisOperation(red, raft)