from typing import List
from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session

from database import get_db
from models.models import PostCreate, PostResponse, PostUpdate
import schema

posts_router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)



@posts_router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = schema.Posts(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@posts_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    db_post = db.query(schema.Posts).filter(schema.Posts.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@posts_router.get("/", response_model=List[PostResponse])
async def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(schema.Posts).all()
    return posts


@posts_router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(schema.Posts).filter(schema.Posts.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    update_data = post.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post


@posts_router.delete("/{post_id}")
async def delete_post(post_id: str, db: Session = Depends(get_db)):
    db_post = db.query(schema.Posts).filter(schema.Posts.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"detail": "Post deleted successfully"}