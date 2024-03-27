# Clean the db0 of the redis server

import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

r.flushdb()