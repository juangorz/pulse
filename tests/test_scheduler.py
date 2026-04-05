import pytest
from unittest.mock import patch
from db.database import SessionLocal
from db.models import Endpoint, Check
from worker.scheduler import enqueue_checks


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def active_endpoints(db):
    e1 = Endpoint(name="Stripe", url="https://api.stripe.com", is_active=True)
    e2 = Endpoint(name="GitHub", url="https://api.github.com", is_active=True)
    e3 = Endpoint(name="Inactivo", url="https://inactivo.com", is_active=False)
    db.add_all([e1, e2, e3])
    db.commit()
    db.refresh(e1)
    db.refresh(e2)
    db.refresh(e3)
    yield e1, e2, e3
    db.query(Check).filter(Check.endpoint_id.in_([e1.id, e2.id, e3.id])).delete()
    db.delete(e1)
    db.delete(e2)
    db.delete(e3)
    db.commit()


def test_enqueue_checks_only_active(active_endpoints):
    e1, e2, e3 = active_endpoints

    with patch("worker.scheduler.Queue") as mock_queue:
        mock_instance = mock_queue.return_value
        enqueue_checks()

        assert mock_instance.enqueue.call_count == 2

        enqueued_ids = [
            call.args[1]
            for call in mock_instance.enqueue.call_args_list
        ]
        assert e1.id in enqueued_ids
        assert e2.id in enqueued_ids
        assert e3.id not in enqueued_ids
