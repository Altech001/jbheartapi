from fastapi import FastAPI
from routes.photos import photo_router
from routes.books import book_router
from routes.bookform import bookform_router
from routes.videos import video_router


from fastapi.middleware.cors import CORSMiddleware


from routes.destinations import destiny_router
from routes.posts import posts_router

import schema
from sqlalchemy.orm import Session
from database import Base, engine, get_db

import httpx
import asyncio
import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APP_URL = os.environ.get("APP_URL", "https://jbheartfelt-api.onrender.com")

PING_INTERVAL = 600


async def keep_alive():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                logger.info(f"Sent keep-alive ping to {APP_URL}/health")
                response = await client.get(f"{APP_URL}/health")
                logger.info(f"Keep-alive response: {response.status_code}")
            except Exception as e:
                logger.error(f"Keep-alive ping failed: {str(e)}")
                
            await asyncio.sleep(PING_INTERVAL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    task = asyncio.create_task(keep_alive())
    yield
    
    task.cancel()



Base.metadata.create_all(engine)

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {
        "status": "ok"
        }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(photo_router)
app.include_router(book_router)
app.include_router(bookform_router)
app.include_router(video_router)


