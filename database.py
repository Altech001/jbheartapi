from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI","postgresql://jb_ydnl_user:fe7mgjQHmmtGTWw5H0sTXaFy7SC5BYBw@dpg-d1n8of0dl3ps73849ue0-a.oregon-postgres.render.com/jb_ydnl")

# DB_URI = "postgresql://postgres:JXIFGLtwzRnjdILHTaCBFWcIdwLQnEmN@shuttle.proxy.rlwy.net:20438/railway"
engine = create_engine(DB_URI, connect_args={"sslmode": "require"})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
