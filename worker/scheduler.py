from rq import Queue
from redis import Redis
from db.database import SessionLocal, settings
from db.models import Endpoint
from worker.checker import run_check


def enqueue_checks():
    db = SessionLocal()
    try:
        redis_conn = Redis.from_url(settings.redis_url)
        queue = Queue(connection=redis_conn)
        endpoints = db.query(Endpoint).filter(Endpoint.is_active == True).all()
        for endpoint in endpoints:
            queue.enqueue(run_check, endpoint.id)
    finally:
        db.close()