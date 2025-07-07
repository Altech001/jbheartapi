from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
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
    max_capacity: int
    required_staff: int
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
    required_staff: int
    gallery: Optional[List[str]] = None
    booked_users: List[UserFull]
    created_at: datetime
    updated_at: Optional[datetime] = None


        
class BookFormCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    guest_capcity: str = "1"
    checkin_date: datetime
    checkout_date: datetime
    special_requests: Optional[str] = None
    activites: Optional[str] = None
    destination: str
    message: str
    
class VideoUpload(BaseModel):
    video_url: str
    video_title: Optional[str] = None
    video_likes: int = 0
    tags: List[str] = []
    description: Optional[str] = None