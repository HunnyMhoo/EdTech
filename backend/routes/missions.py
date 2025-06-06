from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional

# Updated imports to reflect service refactoring
from backend.models.daily_mission import DailyMissionDocument, MissionStatus
from backend.services.mission_service import get_todays_mission_for_user
from backend.services.mission_progress_service import update_mission_progress
from backend.models.api_responses import MissionResponse, ErrorResponse
from backend.dependencies import get_mission_repository, get_question_repository
from backend.repositories.mission_repository import MissionRepository
from backend.repositories.question_repository import QuestionRepository

# Pydantic model for the request body of progress update
from pydantic import BaseModel

class MissionProgressUpdatePayload(BaseModel):
    current_question_index: int
    answers: List[Dict[str, Any]]
    status: Optional[MissionStatus] = None


router = APIRouter()

# Placeholder for user authentication - this was unused and can be removed
# async def get_current_user_id() -> str:
#     """Simulates getting the current user ID. Replace with actual authentication logic."""
#     return "test_user_123" # Hardcoded for now

@router.get("/missions/daily/{user_id}", response_model=MissionResponse[DailyMissionDocument])
async def get_daily_mission_for_user(
    user_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
    question_repo: QuestionRepository = Depends(get_question_repository)
):
    """
    Retrieve today's mission (UTC+7) for the specified user,
    including any progress.
    """
    try:
        mission = await get_todays_mission_for_user(
            user_id=user_id,
            mission_repo=mission_repo,
            question_repo=question_repo
        )
        
        if mission:
            return MissionResponse[DailyMissionDocument](
                status="success", 
                data=mission, # FastAPI will serialize DailyMissionDocument
                message="Today's mission retrieved successfully."
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"No mission found for user {user_id} for today (UTC+7)."
            )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.put("/missions/daily/{user_id}/progress", response_model=MissionResponse[DailyMissionDocument])
async def update_daily_mission_progress(
    user_id: str,
    payload: MissionProgressUpdatePayload,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """
    Update the progress of today's mission for the specified user.
    """
    try:
        updated_mission = await update_mission_progress(
            user_id=user_id,
            current_question_index=payload.current_question_index,
            answers=payload.answers,
            status=payload.status,
            mission_repo=mission_repo
        )
        
        if updated_mission:
            return MissionResponse[DailyMissionDocument](
                status="success",
                data=updated_mission,
                message="Mission progress updated successfully."
            )
        else:
            raise HTTPException(
                status_code=404, # Or 400 if input was bad but mission existed
                detail=f"Failed to update progress for user {user_id}. Mission for today not found or update failed."
            )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while updating progress: {str(e)}"
        )

# Ensure the router can be included in a main app file (example from original)
# from fastapi import FastAPI
# from backend.routes import missions
# app = FastAPI()
# app.include_router(missions.router, prefix="/api") 