from pydantic import BaseModel, ConfigDict

from app.models.challenge import ChallengeCategory


class OrganizationCompetencyCreate(BaseModel):
    category: ChallengeCategory


class OrganizationCompetencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    category: ChallengeCategory