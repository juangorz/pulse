from db.models import Endpoint, Check


def test_endpoint_model_fields():
    endpoint = Endpoint(name="Stripe API", url="https://api.stripe.com/v1/health")
    assert endpoint.name == "Stripe API"
    assert endpoint.url == "https://api.stripe.com/v1/health"
    assert endpoint.interval_seconds == 60
    assert endpoint.is_active is True


def test_check_model_fields():
    check = Check(endpoint_id=1, is_up=True, status_code=200, latency_ms=45.3)
    assert check.is_up is True
    assert check.status_code == 200
    assert check.latency_ms == 45.3