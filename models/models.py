from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from datetime import datetime


class TripStatus(str, Enum):
    ACTIVE = "active"
    PROGRESS = "progress"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class UserMinimal(BaseModel):
    user_id: str
    name: str

class UserFull(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str] = None
    is_admin: bool
    trip_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class TripCreate(BaseModel):
    destination: str
    price: float = 0.0
    description: Optional[str] = None
    image_url: Optional[str] = None
    start_date: datetime
    end_date: datetime
    ratings: float = 0.0
    max_capacity: int
    required_staff: int
    status: TripStatus = TripStatus.ACTIVE
    gallery: Optional[List[str]] = None

class TripResponse(BaseModel):
    id: str
    destination: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: TripStatus
    max_capacity: int
    ratings: float = 0.0
    required_staff: int
    gallery: Optional[List[str]] = None
    booked_users: List[UserFull]
    created_at: datetime
    updated_at: Optional[datetime] = None


        
class BookFormCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    guest_capacity: str = "1"
    checkin_date: datetime
    checkout_date: datetime
    special_requests: Optional[str] = "None"
    activities: Optional[str] = "None"
    destination: str
    message: str

class BookFormUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    guest_capacity: Optional[str] = None
    checkin_date: Optional[datetime] = None
    checkout_date: Optional[datetime] = None
    special_requests: Optional[str] = None
    activities: Optional[str] = None
    destination: Optional[str] = None
    message: Optional[str] = None

class BookFormResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    guest_capacity: str
    checkin_date: datetime
    checkout_date: datetime
    special_requests: Optional[str]
    activities: Optional[str]
    destination: str
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
    
class VideoUpload(BaseModel):
    video_url: str
    video_title: Optional[str] = None
    video_likes: int = 0
    tags: List[str] = []
    description: Optional[str] = None
    

class PostCreate(BaseModel):
    title: str
    content: str
    metadata: Dict = {}
    thumbnail: Dict = {}
    comment: Optional[str] = None
    likes: int = 0
    author_name: str
    is_published: bool = False

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None
    thumbnail: Optional[Dict] = None
    comment: Optional[str] = None
    likes: Optional[int] = None
    author_name: Optional[str] = None
    is_published: Optional[bool] = None

class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    metadata: Dict
    thumbnail: Dict
    comment: Optional[str]
    likes: int
    author_name: str
    created_at: str
    updated_at: str
    is_published: bool

    class Config:
        orm_mode = True
        
        
        
#############
# Pydantic schemas for validation
class DestinationCreate(BaseModel):
    title: str = ""
    description: str = "Home to JB Tours"
    key_highlights: List[str] = [
        "Mountain gorilla trekking",
        "UNESCO World Heritage Site",
        "348 species of birds",
        "Ancient forest ecosystem"
    ]
    ratings: float = 0.0
    d_images: Dict = {}

class DestinationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    key_highlights: Optional[List[str]] = None
    ratings: Optional[float] = None
    d_images: Optional[Dict] = None

class DestinationResponse(BaseModel):
    id: str
    title: str
    description: str
    key_highlights: List[str]
    ratings: float
    d_images: Dict

    class Config:
        orm_mode = True