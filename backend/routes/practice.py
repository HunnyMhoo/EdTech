from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.models.practice_session import PracticeSession
from backend.models.api_responses import MissionResponse
from backend.services.practice_service import (
    create_practice_session,
    get_practice_session,
    submit_practice_answer,
    get_practice_session_summary,
    get_available_practice_topics,
    PracticeServiceError,
    InsufficientQuestionsError,
    SessionNotFoundError,
    SessionAlreadyCompletedError
)
from backend.dependencies import get_question_repository, get_practice_repository
from backend.repositories.question_repository import QuestionRepository
from backend.repositories.practice_repository import PracticeRepository

router = APIRouter(
    prefix="/practice",
    tags=["Practice"],
)

# Request/Response models
class CreatePracticeSessionRequest(BaseModel):
    topic: str
    question_count: int = 5

class SubmitPracticeAnswerRequest(BaseModel):
    question_id: str
    answer: Any

class PracticeSessionResponse(BaseModel):
    session_id: str
    topic: str
    question_count: int
    questions: List[Dict[str, Any]]
    status: str

# API Endpoints

@router.get("/topics", response_model=MissionResponse)
async def get_practice_topics(
    question_repo: QuestionRepository = Depends(get_question_repository)
):
    """
    Get all available topics for practice with question counts.
    """
    try:
        topics = await get_available_practice_topics(question_repo)
        return MissionResponse(
            status="success",
            message="Practice topics retrieved successfully.",
            data=topics
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get practice topics: {str(e)}")

@router.post("/sessions", response_model=MissionResponse)
async def create_session(
    user_id: str,
    request: CreatePracticeSessionRequest,
    question_repo: QuestionRepository = Depends(get_question_repository),
    practice_repo: PracticeRepository = Depends(get_practice_repository)
):
    """
    Create a new practice session for a user.
    
    Query Parameters:
    - user_id: The user ID
    
    Request Body:
    - topic: The topic to practice
    - question_count: Number of questions (1-20, default: 5)
    """
    try:
        session = await create_practice_session(
            user_id=user_id,
            topic=request.topic,
            question_count=request.question_count,
            question_repo=question_repo,
            practice_repo=practice_repo
        )
        
        # Format session for response
        session_data = {
            "session_id": session.session_id,
            "topic": session.topic,
            "question_count": session.question_count,
            "questions": [q.model_dump() for q in session.questions],
            "status": session.status,
            "created_at": session.created_at.isoformat()
        }
        
        return MissionResponse(
            status="success",
            message="Practice session created successfully.",
            data=session_data
        )
        
    except InsufficientQuestionsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PracticeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create practice session: {str(e)}")

@router.get("/sessions/{session_id}", response_model=MissionResponse)
async def get_session(
    session_id: str,
    practice_repo: PracticeRepository = Depends(get_practice_repository)
):
    """
    Get a practice session by ID.
    """
    try:
        session = await get_practice_session(session_id, practice_repo)
        
        # Format session for response
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "topic": session.topic,
            "question_count": session.question_count,
            "questions": [q.model_dump() for q in session.questions],
            "answers": [a.model_dump() for a in session.answers],
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
        
        return MissionResponse(
            status="success",
            message="Practice session retrieved successfully.",
            data=session_data
        )
        
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get practice session: {str(e)}")

@router.post("/sessions/{session_id}/submit-answer")
async def submit_answer(
    session_id: str,
    request: SubmitPracticeAnswerRequest,
    practice_repo: PracticeRepository = Depends(get_practice_repository)
):
    """
    Submit an answer for a practice question.
    """
    try:
        feedback = await submit_practice_answer(
            session_id=session_id,
            question_id=request.question_id,
            user_answer=request.answer,
            practice_repo=practice_repo
        )
        
        return {
            "status": "success",
            "message": "Answer submitted successfully.",
            "feedback": feedback
        }
        
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAlreadyCompletedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PracticeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@router.get("/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    practice_repo: PracticeRepository = Depends(get_practice_repository)
):
    """
    Get summary statistics for a practice session.
    """
    try:
        summary = await get_practice_session_summary(session_id, practice_repo)
        
        return {
            "status": "success",
            "message": "Practice session summary retrieved successfully.",
            "data": summary
        }
        
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session summary: {str(e)}")

@router.get("/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by session status"),
    limit: int = Query(10, ge=1, le=50, description="Number of sessions to return"),
    practice_repo: PracticeRepository = Depends(get_practice_repository)
):
    """
    Get practice sessions for a user.
    """
    try:
        from backend.models.practice_session import PracticeSessionStatus
        
        status_filter = None
        if status:
            try:
                status_filter = PracticeSessionStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        sessions = await practice_repo.get_user_sessions(user_id, status_filter, limit)
        
        # Format sessions for response
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "session_id": session.session_id,
                "topic": session.topic,
                "question_count": session.question_count,
                "status": session.status,
                "correct_count": session.correct_count,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            })
        
        return {
            "status": "success",
            "message": "User practice sessions retrieved successfully.",
            "data": sessions_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user sessions: {str(e)}")

@router.get("/users/{user_id}/stats")
async def get_user_practice_stats(
    user_id: str,
    practice_repo: PracticeRepository = Depends(get_practice_repository)
):
    """
    Get aggregated practice statistics for a user.
    """
    try:
        stats = await practice_repo.get_user_stats(user_id)
        
        return {
            "status": "success",
            "message": "User practice statistics retrieved successfully.",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}") 