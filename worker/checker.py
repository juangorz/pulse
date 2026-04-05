import httpx
from db.database import SessionLocal
from db.models import Endpoint, Check


def run_check(endpoint_id: int) -> Check:
    db = SessionLocal()
    try:
        endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()

        try:
            response = httpx.get(endpoint.url, timeout=10)
            check = Check(
                endpoint_id=endpoint_id,
                status_code=response.status_code,
                latency_ms=response.elapsed.total_seconds() * 1000,
                is_up=response.status_code < 400,
            )
        except Exception as e:
            check = Check(
                endpoint_id=endpoint_id,
                is_up=False,
                error=str(e),
            )

        db.add(check)
        db.commit()
        db.refresh(check)
        return check
    finally:
        db.close()