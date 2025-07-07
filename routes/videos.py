from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session
from database import get_db

import schema
from models.models import VideoUpload


video_router = APIRouter(
    prefix="/videos",
    tags=["videos"],
)

@video_router.post('/upload')
async def video_upload(video: VideoUpload, db: Session = Depends(get_db)):
    video_entry = schema.VideoGallery(**video.model_dump())
    
    db.add(video_entry)
    db.commit()
    db.refresh(video_entry)
    if not video_entry.video_url:
        raise HTTPException(status_code=400, detail="Video URL is required")
    
    return video_entry

@video_router.get('/list')
async def list_videos(db: Session = Depends(get_db)):
    videos = db.query(schema.VideoGallery).all()
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found")
    
    return videos

@video_router.get('/{video_id}')
async def get_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(schema.VideoGallery).filter(schema.VideoGallery.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video

@video_router.delete('/{video_id}')
async def delete_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(schema.VideoGallery).filter(schema.VideoGallery.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    db.delete(video)
    db.commit()
    
    return {"detail": "Video deleted successfully"}

@video_router.put('/{video_id}')
async def update_video(video_id: str, video: VideoUpload, db: Session = Depends(get_db)):
    db_video = db.query(schema.VideoGallery).filter(schema.VideoGallery.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    for key, value in video.model_dump().items():
        setattr(db_video, key, value)
    
    db.commit()
    db.refresh(db_video)
    
    return db_video