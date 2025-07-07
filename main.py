from fastapi import FastAPI
from routes.photos import photo_router
from routes.books import book_router
from routes.bookform import bookform_router
from routes.videos import video_router

from fastapi.middleware.cors import CORSMiddleware


import schema
from sqlalchemy.orm import Session
from database import Base, engine, get_db

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],     # Allow all headers
)

app.include_router(photo_router)
app.include_router(book_router)
app.include_router(bookform_router)
app.include_router(video_router)


