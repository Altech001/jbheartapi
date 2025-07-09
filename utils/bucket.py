from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError
import requests
import os
from dotenv import load_dotenv
from .config import get_s3_client, AWS_BUCKET_NAME, logger
from utils.image_converter import process_file_for_upload

load_dotenv()

# Use the configured s3_client from config
s3_client = get_s3_client()

async def upload_file_to_s3(file: UploadFile, folder: str = None, object_name: str = None):
    if object_name is None:
        object_name = file.filename

    if folder:
        folder = folder.rstrip('/')
        object_name = f"{folder}/{object_name}"

    try:
        # Process the file for compression or optimization
        processed_content, content_type, content_encoding = await process_file_for_upload(file)

        # Prepare parameters for S3 put_object
        put_params = {
            'Bucket': AWS_BUCKET_NAME,
            'Key': object_name,
            'Body': processed_content,
            'ContentType': content_type
        }
        if content_encoding:
            put_params['ContentEncoding'] = content_encoding

        # Upload the processed file to S3
        response = s3_client.put_object(**put_params)

        # Generate path-style public URL
        region = os.getenv('AWS_REGION', 'eu-north-1')
        public_url = f"https://s3.{region}.amazonaws.com/{AWS_BUCKET_NAME}/{object_name}"

        # Verify public access using path-style URL
        verify_response = requests.head(public_url)
        if verify_response.status_code != 200:
            raise Exception("Uploaded file is not publicly accessible. Check bucket policy.")

        return {
            "success": True,
            "key": object_name,
            "etag": response.get('ETag'),
            "public_url": public_url,  # Return direct public URL
            "compressed": bool(content_encoding)
        }
    
    except ClientError as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")
    except Exception as e:
        logger.error(f"Error verifying public URL or processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await file.close()