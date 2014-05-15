"""start_worker
Start a single rq worker to watch the queue database.
A worker is only started if this file is called directly.
Importing this module is useful for accessing `conn`, the Redis connection.
"""
import os
import urlparse
from redis import Redis
from rq import Worker, Queue, Connection

listen = ['default']

# REDIS_URL is defined in .env and loaded into the environment by Honcho
redis_url = os.getenv('REDIS_URL')
if not redis_url:
    raise RuntimeError('Specify a REDIS_URL in .env')

urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
