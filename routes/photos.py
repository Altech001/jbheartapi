from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import requests
from utils.config import get_s3_client, AWS_BUCKET_NAME
from botocore.exceptions import ClientError

photo_router = APIRouter(
    prefix="/photos",
    tags=["Photo Gallery"],
)

from database import get_db
import schema
from utils.bucket import upload_file_to_s3

@photo_router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    image_title: str = None,
    description: str = None,
    image_location: str = None,
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    try:
        result = await upload_file_to_s3(file, folder="gallery", object_name=file.filename)
        image_url = result.get("public_url")  # Now a path-style URL

        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to get public URL.")

        new_photo = schema.PhotoGallery(
            image_url=image_url,
            image_title=image_title,
            description=description,
            image_location=image_location,
        )
        
        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)

        return new_photo

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@photo_router.get("/gallery")
def display_gallery(db: Session = Depends(get_db)):
    photo_gallery = db.query(schema.PhotoGallery).all()
    
    if not photo_gallery:
        return JSONResponse(status_code=404, content={"detail": "No photos found in the gallery."})
    
    return photo_gallery

@photo_router.post("/photos/{photo_id}/like")
async def like_photo(photo_id: str, db: Session = Depends(get_db)):
    photo = db.query(schema.PhotoGallery).filter(schema.PhotoGallery.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    photo.image_likes += 1
    db.commit()
    db.refresh(photo)
    return {"message": "Photo liked", "likes": photo.image_likes}

@photo_router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: str, db: Session = Depends(get_db)):
    """
    Delete a photo from the gallery and optionally from S3.
    """
    photo = db.query(schema.PhotoGallery).filter(schema.PhotoGallery.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        # Extract the object key from the image_url (path-style: https://s3.<region>.amazonaws.com/<bucket>/<key>)
        image_url = photo.image_url
        object_key = image_url.replace(f"https://s3.eu-north-1.amazonaws.com/{AWS_BUCKET_NAME}/", "")

        # Delete the object from S3
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=object_key)

        # Delete the record from the database
        db.delete(photo)
        db.commit()

        return {"message": "Photo deleted successfully"}
    
    except ClientError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete file from S3: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting photo: {str(e)}")