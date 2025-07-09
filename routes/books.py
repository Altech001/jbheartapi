# from fastapi import APIRouter, HTTPException, Depends
# from typing import List

# from sqlalchemy.orm import Session
# from fastapi import Depends
# from database import get_db

# import schema
from models.models import TripCreate, TripResponse, UserCreate, UserMinimal, UserFull, TripStatus
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.params import Depends
from models.models import UserCreate, TripResponse
import schema
from database import get_db
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv
import os
import jinja2
import logging
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



load_dotenv()

book_router = APIRouter(
    prefix="/books",
    tags=["books"],
)


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False") == "True",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


template_loader = jinja2.FileSystemLoader(searchpath="./template")
template_env = jinja2.Environment(loader=template_loader)



async def send_booking_confirmation_email(booking_data: dict, background_tasks: BackgroundTasks):
    try:
        
        template = template_env.get_template("tripbook.html")
        html_content = template.render(**booking_data)
        
        message = MessageSchema(
            subject="Your Trip Booking Confirmation with JB HeartFelt Tours",
            recipients=[booking_data["email"]],
            body=html_content,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@book_router.post("/book/{trip_id}", response_model=TripResponse)
async def book_trip(trip_id: str, user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        
        db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
        if not db_trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        if db_trip.status != TripStatus.ACTIVE.value:
            raise HTTPException(status_code=400, detail="Trip is not active for booking")
        
        
        booked_count = db.query(schema.User).filter(schema.User.trip_id == trip_id).count()
        if booked_count + user.guest_capacity > db_trip.max_capacity:
            raise HTTPException(status_code=400, detail="Trip is fully booked or guest capacity exceeds limit")
        
        
        db_user = schema.User(
            name=user.name,
            email=user.email,
            guest_capacity=user.guest_capacity,
            total_price=user.total_price,
            phone=user.phone,
            trip_id=trip_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.refresh(db_trip)
        
        booking_data = {
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone or "N/A",
            "guest_capacity": db_user.guest_capacity,
            "total_price": db_user.total_price,
            "destination": db_trip.destination,
            "start_date": db_trip.start_date.strftime("%Y-%m-%d") if db_trip.start_date else "N/A",
            "trip_id": db_trip.id
        }
        
        
        await send_booking_confirmation_email(booking_data, background_tasks)
        return db_trip
    except Exception as e:
        logger.error(f"Booking error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process booking: {str(e)}")



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

# @book_router.post("/book/{trip_id}", response_model=TripResponse)
# async def book_trip(trip_id: str, user: UserCreate, db: Session = Depends(get_db)):
#     db_trip = db.query(schema.Trip).filter(schema.Trip.id == trip_id).first()
#     if not db_trip:
#         raise HTTPException(status_code=404, detail="Trip not found")
#     if db_trip.status != TripStatus.ACTIVE.value:
#         raise HTTPException(status_code=400, detail="Trip is not active for booking")
#     booked_count = db.query(schema.User).filter(schema.User.trip_id == trip_id).count()
#     if booked_count >= db_trip.max_capacity:
#         raise HTTPException(status_code=400, detail="Trip is fully booked")
    
#     db_user = schema.User(
#         name=user.name,
#         email=user.email,
#         guest_capacity= user.guest_capacity,
#         total_price= user.total_price,
#         phone=user.phone,
#         trip_id=trip_id
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     db.refresh(db_trip)
#     return db_trip

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

