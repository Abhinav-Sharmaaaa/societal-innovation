from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/rewards",
    tags=["Rewards"],
)

# Mocked Data for Rewards Catalog
MOCK_REWARDS_CATALOG = [
    {
        "id": "reward-1",
        "business": "Local Coffee Shop",
        "title": "Free Coffee",
        "points_cost": 50,
    },
    {
        "id": "reward-2",
        "business": "City Transit",
        "title": "1-Day Bus Pass",
        "points_cost": 100,
    },
    {
        "id": "reward-3",
        "business": "Community Center",
        "title": "Free Fitness Class",
        "points_cost": 200,
    }
]

class RedeemRequest(BaseModel):
    reward_id: str

@router.get("/catalog")
def get_rewards_catalog():
    return MOCK_REWARDS_CATALOG

@router.post("/redeem")
def redeem_reward(request: RedeemRequest):
    # Find the reward
    reward = next((r for r in MOCK_REWARDS_CATALOG if r["id"] == request.reward_id), None)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
        
    # Mocking a successful redemption
    # Normally we would deduct points from the current user and record the redemption
    return {
        "id": str(uuid.uuid4()),
        "reward_id": reward["id"],
        "points_spent": reward["points_cost"],
        "remaining_points": 9999,  # Mock remaining points
        "redeemed_at": datetime.utcnow().isoformat()
    }
