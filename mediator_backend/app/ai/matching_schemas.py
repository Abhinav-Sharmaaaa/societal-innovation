from pydantic import BaseModel, Field


class UniversityMatchRecommendation(BaseModel):
    rank: int = Field(ge=1, le=3)

    organization_id: int
    organization_name: str

    score: float = Field(
        ge=0.0,
        le=100.0,
    )

    competency_match_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    capability_match_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    text_relevance_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    location_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    matched_competencies: list[str]

    matched_capabilities: list[str]

    explanation: str


class UniversityMatchingResponse(BaseModel):
    rfp_id: int
    challenge_id: int

    recommendations: list[
        UniversityMatchRecommendation
    ]

    total_candidates_evaluated: int