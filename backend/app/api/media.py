import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(
    prefix="/media",
    tags=["Media"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import json
from app.services.file_service import save_upload

@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    try:
        # save_upload handles Cloudinary for images, local for others
        file_metadata = await save_upload(file)
        
        # We stringify the metadata as the 'media_id' so the mobile app
        # can just pass it back to POST /challenges in media_ids array.
        # This avoids needing a temporary DB table.
        metadata_str = json.dumps({
            "original_filename": file_metadata["original_filename"],
            "stored_filename": file_metadata["stored_filename"],
            "file_size": file_metadata["file_size"],
            "content_type": file_metadata["content_type"],
            "evidence_type": file_metadata["evidence_type"].value,
            "file_url": file_metadata["file_url"]
        })
        
        return {"media_id": metadata_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
