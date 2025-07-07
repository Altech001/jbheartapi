from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from models.models import BookFormCreate
import schema
from database import get_db
from sqlalchemy.orm import Session


bookform_router = APIRouter(
    prefix="/bookform",
    tags=["bookform"],
)


@bookform_router.post("/submit")
async def submit_book_form(book: BookFormCreate, db: Session = Depends(get_db) ):

    book_form = schema.BookForm(**book.model_dump())
    db.add(book_form)
    db.commit()
    db.refresh(book_form)
    return book_form


