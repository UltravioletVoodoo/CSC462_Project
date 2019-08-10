#https://github.com/andymccurdy/redis-py
#https://github.com/bakwc/PySyncObj
#https://realpython.com/intro-to-python-threading/#what-is-a-thread
#https://redislabs.com/ebook/appendix-a/a-3-installing-on-windows/a-3-2-installing-redis-on-window/

import redis
import pysyncobj
import threading
import sys
import argparse
import json
from pysyncobj import SyncObj, replicated
from flask import Flask, escape, request, render_template

app = Flask(__name__, static_url_path='', static_folder='web/static')
red = None

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

    def setRedis(self, key, value):
        toRedis = {
            "command": "set",
            "key":     key,
            "value":   value
        }
        self.addRedis(toRedis)

#if there is an unapplied command, apply it
def updateRedis(red, raft):
    localCount = 0
    while(True):
        if localCount < raft.getIndex():
            processCommand(red, raft.getHistory()[localCount])
            localCount += 1

#process a command, might want to make this better
def processCommand(red, command):
    if command["command"] == "set":
        red.set(command["key"], command["value"])
    elif command["command"] == "get":
        #nop
        pass
    else:
        print("ProcessCommand: oops")

#gets stuff from command line, and responds apropriately
def commandLineOperation(raft):
    global red

    print("Commands: get, set, force, info, exit")
    
    while(True):
        command = input(">> ")
        #display a value
        if command == "get":
            commandGet = input("get>> ")
            print(red.get(commandGet))
        #modify local database without going
        #through raft, take this out once 
        #testing is done
        elif command == "force":
            commandSet = input("set>> ")
            commandSetTo = input("set:to>> ")
            print(red.set(commandSet, commandSetTo))
        #set a key value pair though raft
        elif command == "set":
            toRedis = {}
            toRedis["command"] = "set"
            toRedis["key"] = input("set>> ")
            toRedis["value"] = input("set:to>> ")
            raft.addRedis(toRedis)
        #get some back end info
        elif command == "info":
            print(raft.isReady())
            print(raft.getHistory())
        elif command == 'exit':
            return
        else:
            print("commandLineOperation: oops")

def handleCommand():
    global red

    # TODO: Fix obvious injection vulnerability
    key = request.args.get("key")
    value = request.args.get("value")
    
    get = []
    if str(request.args.get("cmd")).lower() == 'get':
        r_get = red.get(key)
        if r_get is None:
            return ('get', None)
        else:
            get.append(r_get.decode('utf-8')) # TODO: encoding may result in errors depending on user input
            return ('get', get)
    elif str(request.args.get("cmd")).lower() == 'set':
        raft.setRedis(key, value)
        return ('set', None)

def prepareArgs():
    def ipPair(arg):
        pair = [x for x in arg.split(':')]
        if(len(pair) is not 2):
            raise argparse.ArgumentTypeError("Must be in format 'ip:port'")
        #Error checking
        pair[1] = int(pair[1])
        return pair[0] + ":" + str(pair[1])

    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs=1, type=int)
    parser.add_argument('partners', type=ipPair, nargs='*')
    parser.add_argument('-i', '--redis-ip', type=str, default="localhost")
    parser.add_argument('-p', '--redis-port', type=int, default=6379)
    parser.add_argument('-s', '--flask-port', type=int, default=5000)
    parser.add_argument('--no-flask', action='store_true')
    parser.add_argument('--api-mode', action='store_true')
    return parser.parse_args()

def initFlask(port=5000):
    global app

    @app.route('/')
    def webRoot():
        return render_template('index.html', get=[], noneReturned=False)

    if args.api_mode:
        @app.route('/request', methods=['GET', 'POST'])
        def apiCommand():
            cmd, get = handleCommand()
            if cmd == 'get':
                toReturn = {}
                toReturn["foundElements"] = get is not None
                toReturn["get"] = get
                return json.dumps(toReturn)
            else: # set
                return '{}'
    else:
        @app.route('/request', methods=['GET', 'POST'])
        def webCommand():
            cmd, get = handleCommand()

            noneReturned = False
            if cmd == 'get':
                if get is None:
                    noneReturned = True
            else: # set
                get = []

            return render_template('index.html', get=get, noneReturned=noneReturned)

    #start flask
    app.run(host='0.0.0.0', port=port)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: %s self_port [partner1_ip:partner1_port ...]' % sys.argv[0])
        sys.exit(-1)

    args = prepareArgs()

    #connect to local redis
    print("Redis address: {}:{}".format(args.redis_ip, args.redis_port))
    red = redis.Redis(host=args.redis_ip, port=args.redis_port, db=0)

    #set up raft for communication
    selfAddr = "localhost:%d" % args.port[0]
    print("Current address: {}".format(selfAddr))
    print("Partner addresses: {}".format(args.partners))
    raft = Raft(selfAddr, args.partners)

    #watch raft to see if another node has updated
    update = threading.Thread(target=updateRedis, args=(red, raft, ), daemon=True)
    update.start()

    if not args.no_flask:
        initFlask(port=args.flask_port)
    else:
        #start getting redis operations from the command line
        commandLineOperation(raft)
