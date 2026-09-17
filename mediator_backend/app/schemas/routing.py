from pydantic import BaseModel


class RoutingCandidate(BaseModel):
    organization_id: int
    organization_name: str
    organization_type: str
    score: float
    reason: str


class AuthorityRoutingResponse(BaseModel):
    recommended_authority_id: int | None
    recommended_authority_name: str | None
    score: float
    reason: str
    candidates: list[RoutingCandidate]