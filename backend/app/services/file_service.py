from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


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
    # Create upload directory
    # --------------------------------------------------------

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Generate secure storage filename
    # --------------------------------------------------------

    original_filename = Path(file.filename).name

    extension = Path(
        original_filename
    ).suffix.lower()

    stored_filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = UPLOAD_DIR / stored_filename

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    file_path.write_bytes(file_content)

    # --------------------------------------------------------
    # Return metadata
    # --------------------------------------------------------

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "content_type": file.content_type,
        "file_size": len(file_content),
        "file_url": f"/uploads/{stored_filename}",
        "evidence_type": get_evidence_type(
            file.content_type
        ),
    }