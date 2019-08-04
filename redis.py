#https://github.com/andymccurdy/redis-py
#https://github.com/bakwc/PySyncObj

import redis
import pysyncobj 

r = redis.Redis(host='localhost', port=6379, db=0)
print(r.set('foo', 'bar'))
print(r.get('foo'))