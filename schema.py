from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text,func
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class Admin(Base):
    __tablename__ = "admin"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    

class PhotoGallery(Base):
    __tablename__ = "photo_gallery"
    id = Column(String(36),  default=lambda: str(uuid.uuid4()),unique=True, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    image_title = Column(String(100), nullable=True)
    description = Column(String, nullable=True)
    image_location= Column(String(100), nullable=True)
    image_likes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
class VideoGallery(Base):
    __tablename__ = "video_gallery"
    id = Column(String(36),  default=lambda: str(uuid.uuid4()),unique=True, primary_key=True, index=True)
    video_title = Column(String(100), nullable=True)
    video_url = Column(String, nullable=False)
    tags= Column(String, nullable=True)
    description = Column(String, nullable=True)
    video_likes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    is_admin = Column(Boolean, default=False)
    
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=True)
    trip = relationship("Trip", back_populates="booked_users")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    destination = Column(String(100), nullable=False)
    price = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    ratings= Column(Float, default=0.0)
    status = Column(String(20), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    required_staff = Column(Integer, nullable=False, default=1)
    gallery = Column(JSONB, nullable=True)
    
    booked_users = relationship("User", back_populates="trip")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BookForm(Base):
    __tablename__ = "book_form"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=True)
    guest_capcity = Column(String, nullable=False , default="1")
    checkin_date = Column(DateTime(timezone=True), nullable=False)
    checkout_date = Column(DateTime(timezone=True), nullable=False)
    special_requests = Column(Text, nullable=True, default="None")
    activites = Column(Text, nullable=True, default="None")
    destination = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


