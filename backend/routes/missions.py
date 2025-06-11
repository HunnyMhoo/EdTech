from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional

# Updated imports to reflect service refactoring
from backend.models.daily_mission import DailyMissionDocument, MissionStatus
from backend.services.mission_service import get_todays_mission_for_user
from backend.services.mission_progress_service import (
    update_mission_progress,
    submit_answer_with_feedback,
    mark_feedback_shown,
    reset_question_for_retry
)
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

class AnswerSubmissionPayload(BaseModel):
    question_id: str
    answer: Any

class FeedbackShownPayload(BaseModel):
    question_id: str

class RetryQuestionPayload(BaseModel):
    question_id: str

router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)

# Placeholder for user authentication - this was unused and can be removed
# async def get_current_user_id() -> str:
#     """Simulates getting the current user ID. Replace with actual authentication logic."""
#     return "test_user_123" # Hardcoded for now

@router.get("/daily/{user_id}", response_model=MissionResponse)
async def get_daily_mission(
    user_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
    question_repo: QuestionRepository = Depends(get_question_repository)
):
    """
    Retrieve or generate today's mission for a user.
    """
    try:
        mission = await get_todays_mission_for_user(user_id, mission_repo, question_repo)
        return MissionResponse(
            status="success",
            message="Daily mission retrieved successfully.",
            data=mission
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get daily mission: {str(e)}")

@router.put("/daily/{user_id}/progress", response_model=MissionResponse)
async def update_daily_mission_progress(
    user_id: str,
    payload: MissionProgressUpdatePayload,
    mission_repo: MissionRepository = Depends(get_mission_repository)
):
    """
    Update the progress of today's mission for a user.
    """
    try:
        updated_mission = await update_mission_progress(
            user_id=user_id,
            current_question_index=payload.current_question_index,
            answers=payload.answers,
            mission_repo=mission_repo
        )
        
        if not updated_mission:
            raise HTTPException(status_code=404, detail="Mission not found for the user.")
        
        return MissionResponse(
            status="success",
            message="Mission progress updated successfully.",
            data=updated_mission
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update mission progress: {str(e)}")

@router.post("/daily/{user_id}/submit-answer")
async def submit_answer(
    user_id: str,
    payload: AnswerSubmissionPayload,
    mission_repo: MissionRepository = Depends(get_mission_repository)
):
    """
    Submit an answer and get immediate feedback.
    """
    try:
        feedback = await submit_answer_with_feedback(
            user_id=user_id,
            question_id=payload.question_id,
            user_answer=payload.answer,
            mission_repo=mission_repo
        )
        
        return {
            "status": "success",
            "message": "Answer submitted successfully.",
            "feedback": feedback
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to submit answer: {str(e)}")

@router.post("/daily/{user_id}/mark-feedback-shown")
async def mark_feedback_viewed(
    user_id: str,
    payload: FeedbackShownPayload,
    mission_repo: MissionRepository = Depends(get_mission_repository)
):
    """
    Mark feedback as shown for a specific question.
    """
    try:
        updated_mission = await mark_feedback_shown(
            user_id=user_id,
            question_id=payload.question_id,
            mission_repo=mission_repo
        )
        
        if not updated_mission:
            raise HTTPException(status_code=404, detail="Mission not found for the user.")
        
        return {
            "status": "success",
            "message": "Feedback marked as shown.",
            "mission_status": updated_mission.status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to mark feedback as shown: {str(e)}")

@router.post("/daily/{user_id}/retry-question")
async def retry_question(
    user_id: str,
    payload: RetryQuestionPayload,
    mission_repo: MissionRepository = Depends(get_mission_repository)
):
    """
    Reset a question for retry.
    """
    try:
        result = await reset_question_for_retry(
            user_id=user_id,
            question_id=payload.question_id,
            mission_repo=mission_repo
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "status": "success",
            "message": "Question reset for retry.",
            "remaining_attempts": result["remaining_attempts"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to reset question: {str(e)}")

# Ensure the router can be included in a main app file (example from original)
# from fastapi import FastAPI
# from backend.routes import missions
# app = FastAPI()
# app.include_router(missions.router, prefix="/api") 