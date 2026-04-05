from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from db.database import get_db
from db.models import Endpoint

app = FastAPI(title="Pulse", description="API monitor")


class EndpointCreate(BaseModel):
    name: str
    url: str
    interval_seconds: int = 60


class EndpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    interval_seconds: int
    is_active: bool


@app.post("/endpoints", response_model=EndpointResponse, status_code=201)
def create_endpoint(data: EndpointCreate, db: Session = Depends(get_db)):
    endpoint = Endpoint(
        name=data.name,
        url=data.url,
        interval_seconds=data.interval_seconds
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


@app.get("/endpoints", response_model=list[EndpointResponse])
def list_endpoints(db: Session = Depends(get_db)):
    return db.query(Endpoint).all()