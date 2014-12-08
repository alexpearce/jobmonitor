"""start_worker
Start a single rq worker to watch the queue database.
A worker is only started if this file is called directly.
"""
import os
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
import redis
import rq

listen = ['default']


def create_connection():
    """Return a redis.Redis instance connected to REDIS_URL."""
    # REDIS_URL is defined in .env and loaded into the environment by Honcho
    redis_url = os.getenv('REDIS_URL')
    # If it's not defined, use the Redis default
    if not redis_url:
        redis_url = 'redis://localhost:6379'
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(redis_url)
    return redis.StrictRedis(
        host=url.hostname,
        port=url.port,
        db=0,
        password=url.password
    )


def work():
    """Start an rq worker on the connection provided by create_connection."""
    with rq.Connection(create_connection()):
        worker = rq.Worker(list(map(rq.Queue, listen)))
        worker.work()

if __name__ == '__main__':
    work()
