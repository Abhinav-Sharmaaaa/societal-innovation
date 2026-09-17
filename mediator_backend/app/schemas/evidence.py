from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.challenge_evidence import EvidenceType


# ============================================================
# Evidence Response
# ============================================================

class EvidenceResponse(BaseModel):
    """
    API response for uploaded challenge evidence.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: int

    evidence_type: EvidenceType

    original_filename: str
    stored_filename: str

    content_type: str | None
    file_size: int | None

    file_url: str | None

    uploaded_by: int

    created_at: datetime