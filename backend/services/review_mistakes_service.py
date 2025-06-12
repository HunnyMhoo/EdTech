from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
import math
from collections import defaultdict

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Answer, Question, ChoiceOption
from backend.models.api_responses import (
    ReviewMistakeItem, 
    ReviewMistakesResponse, 
    GroupedReviewMistakesResponse,
    PaginationInfo
)
from backend.repositories.mission_repository import MissionRepository
from backend.services.utils import get_current_time_in_target_timezone


class ReviewMistakesService:
    """Service for handling review mistakes functionality with advanced features"""
    
    def __init__(self, mission_repo: MissionRepository):
        self.mission_repo = mission_repo
    
    async def get_user_mistakes(
        self,
        user_id: str,
        page: int = 1,
        items_per_page: int = 20,
        group_by: Optional[str] = None,  # 'date' or 'topic'
        skill_area_filter: Optional[str] = None
    ) -> ReviewMistakesResponse | GroupedReviewMistakesResponse:
        """
        Retrieves paginated user mistakes from completed and archived missions.
        
        Args:
            user_id: The user ID
            page: Page number (1-based)
            items_per_page: Number of items per page
            group_by: Grouping method ('date' or 'topic')
            skill_area_filter: Optional filter by skill area
        
        Returns:
            Paginated response with mistakes data
        """
        # Get all completed and archived missions for the user
        missions = await self._get_eligible_missions(user_id)
        
        # Extract mistakes from missions
        all_mistakes = await self._extract_mistakes_from_missions(missions)
        
        # Apply skill area filter if provided
        if skill_area_filter:
            all_mistakes = [m for m in all_mistakes if m.skill_area == skill_area_filter]
        
        total_mistakes = len(all_mistakes)
        
        if total_mistakes == 0:
            empty_pagination = PaginationInfo(
                current_page=1,
                total_pages=0,
                total_items=0,
                items_per_page=items_per_page,
                has_next=False,
                has_previous=False
            )
            
            if group_by:
                return GroupedReviewMistakesResponse(
                    grouped_mistakes={},
                    pagination=empty_pagination,
                    total_mistakes=0,
                    group_counts={}
                )
            else:
                return ReviewMistakesResponse(
                    mistakes=[],
                    pagination=empty_pagination,
                    total_mistakes=0
                )
        
        # Handle grouping
        if group_by:
            return await self._get_grouped_mistakes(
                all_mistakes, page, items_per_page, group_by
            )
        else:
            return await self._get_paginated_mistakes(
                all_mistakes, page, items_per_page
            )
    
    async def get_available_skill_areas(self, user_id: str) -> List[str]:
        """
        Get list of skill areas where user has made mistakes.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of available skill areas
        """
        missions = await self._get_eligible_missions(user_id)
        mistakes = await self._extract_mistakes_from_missions(missions)
        
        skill_areas = list(set(mistake.skill_area for mistake in mistakes))
        return sorted(skill_areas)
    
    async def _get_eligible_missions(self, user_id: str) -> List[DailyMissionDocument]:
        """Get all completed and archived missions for a user"""
        eligible_statuses = [MissionStatus.COMPLETE, MissionStatus.ARCHIVED]
        missions = []
        
        for status in eligible_statuses:
            status_missions = await self.mission_repo.find_missions_by_status(user_id, status)
            missions.extend(status_missions)
        
        # Sort by date descending (most recent first)
        missions.sort(key=lambda m: m.date, reverse=True)
        return missions
    
    async def _extract_mistakes_from_missions(
        self, missions: List[DailyMissionDocument]
    ) -> List[ReviewMistakeItem]:
        """Extract incorrect answers from missions"""
        mistakes = []
        
        for mission in missions:
            mission_mistakes = await self._extract_mistakes_from_single_mission(mission)
            mistakes.extend(mission_mistakes)
        
        return mistakes
    
    async def _extract_mistakes_from_single_mission(
        self, mission: DailyMissionDocument
    ) -> List[ReviewMistakeItem]:
        """Extract mistakes from a single mission"""
        mistakes = []
        
        # Create lookup for questions by ID
        questions_by_id = {q.question_id: q for q in mission.questions}
        
        for answer in mission.answers:
            # Only include incorrect answers
            if not answer.is_correct and answer.current_answer:
                question = questions_by_id.get(answer.question_id)
                if not question:
                    continue
                
                # Find user's answer text and correct answer text
                user_answer_text = self._get_choice_text(question.choices, answer.current_answer)
                correct_answer_text = self._get_choice_text(question.choices, question.correct_answer_id)
                
                mistake_item = ReviewMistakeItem(
                    question_id=question.question_id,
                    question_text=question.question_text,
                    skill_area=question.skill_area,
                    difficulty_level=question.difficulty_level,
                    choices=[
                        {"id": choice.id, "text": choice.text} 
                        for choice in question.choices
                    ],
                    user_answer_id=str(answer.current_answer),
                    user_answer_text=user_answer_text,
                    correct_answer_id=question.correct_answer_id,
                    correct_answer_text=correct_answer_text,
                    explanation=question.feedback_th,
                    mission_date=mission.date,
                    mission_completion_date=mission.updated_at,
                    attempt_count=answer.attempt_count
                )
                
                mistakes.append(mistake_item)
        
        return mistakes
    
    def _get_choice_text(self, choices: List[ChoiceOption], choice_id: str) -> str:
        """Get choice text by ID"""
        for choice in choices:
            if choice.id == choice_id:
                return choice.text
        return "Unknown"
    
    async def _get_paginated_mistakes(
        self, mistakes: List[ReviewMistakeItem], page: int, items_per_page: int
    ) -> ReviewMistakesResponse:
        """Get paginated mistakes without grouping"""
        total_items = len(mistakes)
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 0
        
        # Calculate pagination
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_mistakes = mistakes[start_idx:end_idx]
        
        pagination_info = PaginationInfo(
            current_page=page,
            total_pages=total_pages,
            total_items=total_items,
            items_per_page=items_per_page,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return ReviewMistakesResponse(
            mistakes=paginated_mistakes,
            pagination=pagination_info,
            total_mistakes=total_items
        )
    
    async def _get_grouped_mistakes(
        self, 
        mistakes: List[ReviewMistakeItem], 
        page: int, 
        items_per_page: int, 
        group_by: str
    ) -> GroupedReviewMistakesResponse:
        """Get grouped and paginated mistakes"""
        # Group mistakes
        grouped = defaultdict(list)
        
        for mistake in mistakes:
            if group_by == 'date':
                # Group by mission date in DD MMM YYYY format
                key = mistake.mission_date.strftime('%d %b %Y')
            elif group_by == 'topic':
                # Group by skill area
                key = mistake.skill_area
            else:
                key = 'All'
            
            grouped[key].append(mistake)
        
        # Convert to regular dict and sort groups
        grouped_dict = dict(grouped)
        
        if group_by == 'date':
            # Sort by date descending (most recent first)
            sorted_keys = sorted(
                grouped_dict.keys(), 
                key=lambda x: datetime.strptime(x, '%d %b %Y'), 
                reverse=True
            )
        else:
            # Sort alphabetically for topics
            sorted_keys = sorted(grouped_dict.keys())
        
        # Create group counts
        group_counts = {key: len(grouped_dict[key]) for key in sorted_keys}
        
        # Paginate groups (not individual items)
        total_groups = len(sorted_keys)
        total_pages = math.ceil(total_groups / items_per_page) if total_groups > 0 else 0
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_keys = sorted_keys[start_idx:end_idx]
        
        # Build final grouped response
        paginated_grouped = {key: grouped_dict[key] for key in paginated_keys}
        
        pagination_info = PaginationInfo(
            current_page=page,
            total_pages=total_pages,
            total_items=total_groups,
            items_per_page=items_per_page,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return GroupedReviewMistakesResponse(
            grouped_mistakes=paginated_grouped,
            pagination=pagination_info,
            total_mistakes=len(mistakes),
            group_counts=group_counts
        ) 