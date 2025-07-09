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
    guest_capacity = Column(Integer, nullable=True)
    total_price = Column(Float, default=0.0)
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
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=True)
    guest_capcity = Column(Integer, nullable=True)
    checkin_date = Column(DateTime(timezone=True), nullable=False)
    checkout_date = Column(DateTime(timezone=True), nullable=True)
    special_requests = Column(Text, nullable=True, default="None")
    activites = Column(Text, nullable=True, default="None")
    destination = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


#########################
class Destinations(Base):
    __tablename__ = "destinations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, default="", nullable=False)
    description = Column(String, default="Home to JB Tours", nullable=False)
    key_highlights = Column(JSONB, default=[
        "Mountain gorilla trekking",
        "UNESCO World Heritage Site",
        "348 species of birds",
        "Ancient forest ecosystem"
    ], nullable=False)
    ratings= Column(Float, default=0.0)
    d_images = Column(JSONB, default={}, nullable=True)
    
    
class Posts(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    post_metadata = Column(JSONB, default=dict, nullable=True)
    thumbnail = Column(JSONB, default=dict, nullable=True)
    comment = Column(Text, nullable=True)
    likes = Column(Integer, default=0, nullable=True)
    
    author_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)