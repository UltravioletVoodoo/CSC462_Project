#https://github.com/andymccurdy/redis-py
#https://github.com/bakwc/PySyncObj
#https://realpython.com/intro-to-python-threading/#what-is-a-thread
#https://redislabs.com/ebook/appendix-a/a-3-installing-on-windows/a-3-2-installing-redis-on-window/

import redis
import pysyncobj 

class Raft(SyncObj):
	def __init__(self, selfNodeAddr, otherNodeAddrs):
        super(TestObj, self).__init__(selfNodeAddr, otherNodeAddrs)
        self.index = 0
		self.history = []
		
	@replicated
    def incIndex(self):
        self.index += 1
        return self.index
		
	def getIndex(self):
		return self.index
	
	@replicated
	def addRedis(self, command):
		self.history.append(command)
		return self.history

def redisOperation(r):
	while(True):
		command = input(">> ")
		if command == "get":
			commandGet = input("get>> ")
			print(r.get(commandGet))
		elif command == "set":
			commandSet = input("set>> ")
			commandSetTo = input("set:to>> ")
			print(r.set(commandSet, commandSetTo))
		else:
			print("oops")

r = redis.Redis(host='localhost', port=6379, db=0)
redisOperation(r)

#print(r.set('foo', 'bar'))
#print(r.get('foo'))