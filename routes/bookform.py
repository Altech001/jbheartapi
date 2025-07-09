from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.params import Depends
from models.models import BookFormCreate, BookFormResponse, BookFormUpdate
import schema
from database import get_db
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from datetime import datetime
from dotenv import load_dotenv
import os
import jinja2
import uuid
from datetime import datetime


load_dotenv()

bookform_router = APIRouter(
    prefix="/bookform",
    tags=["Bookform"],
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

def calculate_price(guest_capacity: int, checkin_date: datetime, checkout_date: datetime, activities: str) -> float:
    
    nights = (checkout_date - checkin_date).days if checkout_date else 1
    nights = max(nights, 1)
    base_price = guest_capacity * nights * 100
    activity_count = len(activities.split(",")) if activities and activities != "None" else 0
    activity_price = activity_count * 50
    return base_price + activity_price

async def send_booking_email(booking_data: dict, background_tasks: BackgroundTasks):
    
    template = template_env.get_template("bookform.html")
    html_content = template.render(**booking_data)
    
    
    message = MessageSchema(
        subject="Your Booking Confirmation with JB HeartFelt Tours",
        recipients=[booking_data["email"]],
        body=html_content,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    

@bookform_router.post("/submit", response_model=BookFormResponse)
async def submit_book_form(book: BookFormCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    
    book_form = schema.BookForm(**book.dict(), id=str(uuid.uuid4()))
    db.add(book_form)
    db.commit()
    db.refresh(book_form)
    
    booking_data = {
        "id": book_form.id,
        "name": book_form.name,
        "email": book_form.email,
        "phone": book_form.phone,
        "guest_capcity": book_form.guest_capcity,
        "checkin_date": book_form.checkin_date.strftime("%Y-%m-%d"),
        "checkout_date": book_form.checkout_date.strftime("%Y-%m-%d") if book_form.checkout_date else "N/A",
        "special_requests": book_form.special_requests,
        "activites": book_form.activites,
        "destination": book_form.destination,
        "message": book_form.message,
        "created_at": book_form.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "total_price": calculate_price(
            book_form.guest_capcity,
            book_form.checkin_date,
            book_form.checkout_date,
            book_form.activites
        )
    }
    
    await send_booking_email(booking_data, background_tasks)
    return book_form


@bookform_router.get("/{book_id}", response_model=BookFormResponse)
async def get_book_form(book_id: str, db: Session = Depends(get_db)):
    book_form = db.query(schema.BookForm).filter(schema.BookForm.id == book_id).first()
    if book_form is None:
        raise HTTPException(status_code=404, detail="Booking form not found")
    return book_form


@bookform_router.get("/", response_model=List[BookFormResponse])
async def get_all_book_forms(db: Session = Depends(get_db)):
    book_forms = db.query(schema.BookForm).all()
    return book_forms


@bookform_router.put("/{book_id}", response_model=BookFormResponse)
async def update_book_form(book_id: str, book: BookFormUpdate, db: Session = Depends(get_db)):
    book_form = db.query(schema.BookForm).filter(schema.BookForm.id == book_id).first()
    if book_form is None:
        raise HTTPException(status_code=404, detail="Booking form not found")
    update_data = book.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book_form, key, value)
    db.commit()
    db.refresh(book_form)
    return book_form


@bookform_router.delete("/{book_id}")
async def delete_book_form(book_id: str, db: Session = Depends(get_db)):
    book_form = db.query(schema.BookForm).filter(schema.BookForm.id == book_id).first()
    if book_form is None:
        raise HTTPException(status_code=404, detail="Booking form not found")
    db.delete(book_form)
    db.commit()
    return {"detail": "Booking form deleted successfully"}

@bookform_router.delete("/delete/all")
async def delete_all_book_forms(db: Session = Depends(get_db)):
    book_forms = db.query(schema.BookForm).all()
    if not book_forms:
        raise HTTPException(status_code=404, detail="No booking forms found to delete")
    for book_form in book_forms:
        db.delete(book_form)
    db.commit()
    return {"detail": "All booking forms deleted successfully"}
