import io
import gzip
from PIL import Image
from fastapi import UploadFile

async def process_file_for_upload(file: UploadFile):
    content = await file.read()
    content_type = file.content_type
    content_encoding = None

    if content_type in ["image/jpeg", "image/png", "image/webp"]:
        try:
            image = Image.open(io.BytesIO(content))
            
            output = io.BytesIO()
            if content_type == "image/jpeg":
                image.save(output, format='JPEG', quality=85, optimize=True)
            elif content_type == "image/png":
                image.save(output, format='PNG', optimize=True)
            elif content_type == "image/webp":
                image.save(output, format='WEBP', quality=85)
            else:
                image.save(output, format=image.format, optimize=True)
            
            content = output.getvalue()
            
        except Exception:
            pass

    elif content_type in ["text/plain", "text/html", "text/css", "application/javascript", "application/json", "text/csv"]:
        output = io.BytesIO()
        with gzip.GzipFile(fileobj=output, mode='wb') as f:
            f.write(content)
        content = output.getvalue()
        content_encoding = 'gzip'

    await file.seek(0)
    
    return content, content_type, content_encoding
