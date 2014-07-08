web: gunicorn webmonitor:create_app
worker: python webmonitor/start_worker.py
redis: redis-server /usr/local/etc/redis.conf
