from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from models.models import BookFormCreate, BookFormResponse, BookFormUpdate
import schema
from database import get_db
from sqlalchemy.orm import Session


bookform_router = APIRouter(
    prefix="/bookform",
    tags=["Bookform"],
)



@bookform_router.post("/submit", response_model=BookFormResponse)
async def submit_book_form(book: BookFormCreate, db: Session = Depends(get_db)):
    book_form = schema.BookForm(**book.dict())
    db.add(book_form)
    db.commit()
    db.refresh(book_form)
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

