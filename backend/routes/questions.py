from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Depends

from backend.models.daily_mission import Question  # Question model now includes choices
from backend.services.mission_service import get_question_details_by_id
from backend.dependencies import get_question_repository
from backend.repositories.question_repository import QuestionRepository

router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)

# Note for integration:
# This router needs to be included in the main FastAPI application.
# For example, in your main.py or app setup file:
# from backend.routes import questions as questions_router
# app.include_router(questions_router.router)

@router.get(
    "/{question_id}", 
    response_model=Question, 
    summary="Get Question Details by ID",
    description="Retrieve the full details of a specific question, including its text, choices, and feedback, by its unique ID."
)
async def get_question_by_id(
    question_id: str = Path(..., description="The unique ID of the question to retrieve.", example="GATQ001"),
    question_repo: QuestionRepository = Depends(get_question_repository)
) -> Question:
    """
    Fetches a question by its ID.

    - **question_id**: The unique identifier for the question.
    """
    question = await get_question_details_by_id(question_id, question_repo)
    if not question:
        raise HTTPException(
            status_code=404, 
            detail=f"Question with ID '{question_id}' not found. Ensure the question exists and the CSV data is correctly loaded."
        )
    return question 