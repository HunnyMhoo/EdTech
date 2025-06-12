from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
import logging

from backend.models.api_responses import (
    MissionResponse, 
    ErrorResponse, 
    ReviewMistakesResponse,
    GroupedReviewMistakesResponse
)
from backend.services.review_mistakes_service import ReviewMistakesService
from backend.repositories.mission_repository import MissionRepository
from backend.dependencies import get_database, get_mission_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/review-mistakes", tags=["review-mistakes"])


def get_review_mistakes_service(
    mission_repo: MissionRepository = Depends(get_mission_repository)
) -> ReviewMistakesService:
    """Dependency to get review mistakes service"""
    return ReviewMistakesService(mission_repo)


@router.get("/{user_id}", response_model=MissionResponse[ReviewMistakesResponse])
async def get_review_mistakes(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    items_per_page: int = Query(20, ge=1, le=50, description="Items per page (max 50)"),
    skill_area: Optional[str] = Query(None, description="Filter by skill area"),
    service: ReviewMistakesService = Depends(get_review_mistakes_service)
):
    """
    Get paginated list of user's mistakes from completed missions.
    Returns mistakes without grouping.
    """
    try:
        result = await service.get_user_mistakes(
            user_id=user_id,
            page=page,
            items_per_page=items_per_page,
            group_by=None,
            skill_area_filter=skill_area
        )
        
        if not isinstance(result, ReviewMistakesResponse):
            raise HTTPException(status_code=500, detail="Unexpected response type")
        
        # Check if user has no mistakes
        if result.total_mistakes == 0:
            return MissionResponse(
                status="success",
                data=result,
                message="Great job! You have no mistakes to review right now."
            )
        
        return MissionResponse(
            status="success",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error fetching review mistakes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch review mistakes")


@router.get("/{user_id}/grouped", response_model=MissionResponse[GroupedReviewMistakesResponse])
async def get_grouped_review_mistakes(
    user_id: str,
    group_by: str = Query(..., regex="^(date|topic)$", description="Group by 'date' or 'topic'"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    items_per_page: int = Query(10, ge=1, le=20, description="Groups per page (max 20)"),
    skill_area: Optional[str] = Query(None, description="Filter by skill area"),
    service: ReviewMistakesService = Depends(get_review_mistakes_service)
):
    """
    Get grouped and paginated list of user's mistakes.
    Groups can be by date or topic (skill_area).
    """
    try:
        result = await service.get_user_mistakes(
            user_id=user_id,
            page=page,
            items_per_page=items_per_page,
            group_by=group_by,
            skill_area_filter=skill_area
        )
        
        if not isinstance(result, GroupedReviewMistakesResponse):
            raise HTTPException(status_code=500, detail="Unexpected response type")
        
        # Check if user has no mistakes
        if result.total_mistakes == 0:
            return MissionResponse(
                status="success",
                data=result,
                message="Great job! You have no mistakes to review right now."
            )
        
        return MissionResponse(
            status="success",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error fetching grouped review mistakes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch grouped review mistakes")


@router.get("/{user_id}/skill-areas", response_model=MissionResponse[List[str]])
async def get_available_skill_areas(
    user_id: str,
    service: ReviewMistakesService = Depends(get_review_mistakes_service)
):
    """
    Get list of skill areas where the user has made mistakes.
    Useful for filtering options.
    """
    try:
        skill_areas = await service.get_available_skill_areas(user_id)
        
        return MissionResponse(
            status="success",
            data=skill_areas
        )
        
    except Exception as e:
        logger.error(f"Error fetching skill areas: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch skill areas")


@router.get("/{user_id}/stats", response_model=MissionResponse[dict])
async def get_review_stats(
    user_id: str,
    service: ReviewMistakesService = Depends(get_review_mistakes_service)
):
    """
    Get summary statistics about user's mistakes.
    """
    try:
        # Get all mistakes to calculate stats
        result = await service.get_user_mistakes(
            user_id=user_id,
            page=1,
            items_per_page=1000,  # Large number to get all
            group_by=None
        )
        
        if not isinstance(result, ReviewMistakesResponse):
            raise HTTPException(status_code=500, detail="Unexpected response type")
        
        # Calculate basic stats
        total_mistakes = result.total_mistakes
        skill_areas = list(set(mistake.skill_area for mistake in result.mistakes))
        
        # Group by difficulty
        difficulty_stats = {}
        for mistake in result.mistakes:
            level = mistake.difficulty_level
            difficulty_stats[level] = difficulty_stats.get(level, 0) + 1
        
        stats = {
            "total_mistakes": total_mistakes,
            "skill_areas_count": len(skill_areas),
            "skill_areas": skill_areas,
            "difficulty_breakdown": difficulty_stats
        }
        
        return MissionResponse(
            status="success",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error fetching review stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch review stats") 