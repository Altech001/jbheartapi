from fastapi import APIRouter, HTTPException, Depends
from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db

import schema
from models.models import TripCreate, TripResponse, UserCreate, UserMinimal, UserFull, TripStatus


book_router = APIRouter(
    prefix="/books",
    tags=["books"],
)

@book_router.post("/trips/", response_model=TripResponse)
async def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    if trip.max_capacity < 1:
        raise HTTPException(status_code=400, detail="Max capacity must be at least 1")
    if trip.required_staff < 0:
        raise HTTPException(status_code=400, detail="Required staff cannot be negative")
    db_trip = schema.Trip(**trip.model_dump())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@book_router.post("/book/{trip_id}", response_model=TripResponse)
async def book_trip(trip_id: str, user: UserCreate, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if db_trip.status != TripStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Trip is not active for booking")
    booked_count = db.query(schema.User).filter(schema.User.trip_id == trip_id).count()
    if booked_count >= db_trip.max_capacity:
        raise HTTPException(status_code=400, detail="Trip is fully booked")
    
    db_user = schema.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        trip_id=trip_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.refresh(db_trip)
    return db_trip

@book_router.get("/book/{trip_id}", response_model=TripResponse)
async def get_booking(trip_id: str, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@book_router.get("/trips/", response_model=List[TripResponse])
async def get_all_trips(db: Session = Depends(get_db)):
    return db.query(schema.Trip).all()

@book_router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: str, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@book_router.get("/trips/{trip_id}/users/minimal", response_model=List[UserMinimal])
async def get_trip_users_minimal(trip_id: str, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    users = db.query(schema.User).filter(schema.User.trip_id == trip_id).all()
    return [UserMinimal(user_id=user.user_id, name=user.name) for user in users]

@book_router.get("/trips/{trip_id}/users/full", response_model=List[UserFull])
async def get_trip_users_full(trip_id: str, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db.query(schema.User).filter(schema.User.trip_id == trip_id).all()

@book_router.put("/trips/{trip_id}/status", response_model=TripResponse)
async def update_trip_status(trip_id: str, status: TripStatus, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db_trip.status = status.value
    db.commit()
    db.refresh(db_trip)
    return db_trip

@book_router.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str, db: Session = Depends(get_db)):
    db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(db_trip)
    db.commit()
    return {"message": "Trip deleted successfully"}

