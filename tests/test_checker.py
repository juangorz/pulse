import pytest
from unittest.mock import patch, MagicMock
from db.database import SessionLocal
from db.models import Check, Endpoint
from worker.checker import run_check


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_endpoint(db):
    endpoint = Endpoint(name="test", url="https://api.stripe.com")
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    yield endpoint
    db.query(Check).filter(Check.endpoint_id == endpoint.id).delete()
    db.delete(endpoint)
    db.commit()


def test_check_endpoint_up(test_endpoint):
    with patch("worker.checker.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.065
        mock_get.return_value = mock_response

        check = run_check(test_endpoint.id)

    assert check.is_up is True
    assert check.status_code == 200
    assert check.latency_ms > 0
    assert check.endpoint_id == test_endpoint.id


def test_check_endpoint_down(test_endpoint):
    with patch("worker.checker.httpx.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")

        check = run_check(test_endpoint.id)

    assert check.is_up is False
    assert check.error == "Connection refused"
    assert check.endpoint_id == test_endpoint.id
