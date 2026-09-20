from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


# ============================================================
# Storage Configuration
# ============================================================

UPLOAD_DIR = Path("uploads")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ============================================================
# Allowed File Types
# ============================================================

ALLOWED_CONTENT_TYPES = {
    # Images
    "image/jpeg",
    "image/png",
    "image/webp",

    # Videos
    "video/mp4",
    "video/webm",
    "video/quicktime",

    # Documents
    "application/pdf",
}


# ============================================================
# Evidence Type Detection
# ============================================================

def get_evidence_type(content_type: str):
    """
    Convert MIME type into the application's EvidenceType enum.
    """

    from app.models.challenge_evidence import EvidenceType

    if content_type.startswith("image/"):
        return EvidenceType.IMAGE

    if content_type.startswith("video/"):
        return EvidenceType.VIDEO

    if content_type == "application/pdf":
        return EvidenceType.DOCUMENT

    return EvidenceType.OTHER


# ============================================================
# Save Upload
# ============================================================

async def save_upload(file: UploadFile) -> dict:
    """
    Validate and store an uploaded file.

    Returns metadata required by ChallengeEvidence.
    """

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:
        raise ValueError("A file must be provided.")

    # --------------------------------------------------------
    # Validate MIME type
    # --------------------------------------------------------

    if not file.content_type:
        raise ValueError("Could not determine file type.")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported file type: {file.content_type}"
        )

    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    file_content = await file.read()

    # --------------------------------------------------------
    # Validate file size
    # --------------------------------------------------------

    if len(file_content) == 0:
        raise ValueError("Uploaded file is empty.")

    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            "File exceeds the maximum allowed size of 50 MB."
        )

    # --------------------------------------------------------
    # Generate secure storage filename
    # --------------------------------------------------------

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()
    stored_filename = f"{uuid4().hex}{extension}"

    evidence_type = get_evidence_type(file.content_type)

    if evidence_type.name == "IMAGE" or evidence_type.value == "IMAGE":
        # Image upload using Cloudinary
        await file.seek(0)
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="image",
            folder="societal_innovation/uploads",
            public_id=stored_filename.split('.')[0]
        )
        file_url = result.get("secure_url")
        file_size = result.get("bytes", len(file_content))
    else:
        # Local upload for other types
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path = UPLOAD_DIR / stored_filename
        file_path.write_bytes(file_content)
        file_url = f"/uploads/{stored_filename}"
        file_size = len(file_content)

    # --------------------------------------------------------
    # Return metadata
    # --------------------------------------------------------

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "content_type": file.content_type,
        "file_size": file_size,
        "file_url": file_url,
        "evidence_type": evidence_type,
    }
