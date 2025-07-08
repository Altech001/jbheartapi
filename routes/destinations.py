from fastapi import APIRouter,HTTPException, Depends
from database import get_db
from models.models import DestinationCreate, DestinationResponse, DestinationUpdate
import schema
from sqlalchemy.orm import Session

from typing import List

destiny_router = APIRouter(
    prefix="/places",
    tags= ["Destinations"]
)


@destiny_router.post("/", response_model=DestinationResponse)
async def create_destination(destination: DestinationCreate, db: Session = Depends(get_db)):
    db_destination = schema.Destinations(**destination.dict())
    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)
    return db_destination


@destiny_router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(destination_id: str, db: Session = Depends(get_db)):
    db_destination = db.query(schema.Destinations).filter(schema.Destinations.id == destination_id).first()
    if db_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    return db_destination


@destiny_router.get("/", response_model=List[DestinationResponse])
async def get_all_destinations(db: Session = Depends(get_db)):
    destinations = db.query(schema.Destinations).all()
    return destinations


@destiny_router.put("/{destination_id}", response_model=DestinationResponse)
async def update_destination(destination_id: str, destination: DestinationUpdate, db: Session = Depends(get_db)):
    db_destination = db.query(schema.Destinations).filter(schema.Destinations.id == destination_id).first()
    if db_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    update_data = destination.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_destination, key, value)
    db.commit()
    db.refresh(db_destination)
    return db_destination


@destiny_router.delete("/{destination_id}")
async def delete_destination(destination_id: str, db: Session = Depends(get_db)):
    db_destination = db.query(schema.Destinations).filter(schema.Destinations.id == destination_id).first()
    if db_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    db.delete(db_destination)
    db.commit()
    return {"detail": "Destination deleted successfully"}

