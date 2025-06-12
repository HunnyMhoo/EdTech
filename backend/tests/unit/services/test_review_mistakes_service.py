import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date, datetime
from typing import List

from backend.services.review_mistakes_service import ReviewMistakesService
from backend.models.daily_mission import (
    DailyMissionDocument, 
    MissionStatus, 
    Question, 
    ChoiceOption, 
    Answer,
    AnswerAttempt
)
from backend.models.api_responses import (
    ReviewMistakeItem,
    ReviewMistakesResponse,
    GroupedReviewMistakesResponse,
    PaginationInfo
)


class TestReviewMistakesService:
    """Test suite for ReviewMistakesService"""
    
    @pytest.fixture
    def mock_mission_repo(self):
        """Mock mission repository"""
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_mission_repo):
        """Create service instance with mocked repository"""
        return ReviewMistakesService(mock_mission_repo)
    
    @pytest.fixture
    def sample_questions(self):
        """Sample questions for testing"""
        return [
            Question(
                question_id="Q1",
                question_text="What is 2+2?",
                skill_area="Mathematics",
                difficulty_level=1,
                choices=[
                    ChoiceOption(id="A", text="3"),
                    ChoiceOption(id="B", text="4"),
                    ChoiceOption(id="C", text="5")
                ],
                correct_answer_id="B",
                feedback_th="The correct answer is 4."
            ),
            Question(
                question_id="Q2",
                question_text="What is the capital of Thailand?",
                skill_area="Geography",
                difficulty_level=2,
                choices=[
                    ChoiceOption(id="A", text="Bangkok"),
                    ChoiceOption(id="B", text="Chiang Mai"),
                    ChoiceOption(id="C", text="Phuket")
                ],
                correct_answer_id="A",
                feedback_th="Bangkok is the capital of Thailand."
            )
        ]
    
    @pytest.fixture
    def sample_missions(self, sample_questions):
        """Sample missions with mistakes for testing"""
        return [
            DailyMissionDocument(
                user_id="user123",
                date=date(2024, 1, 15),
                questions=sample_questions,
                status=MissionStatus.COMPLETE,
                answers=[
                    Answer(
                        question_id="Q1",
                        current_answer="A",  # Wrong answer
                        is_correct=False,
                        attempt_count=2,
                        attempts_history=[
                            AnswerAttempt(answer="C", is_correct=False),
                            AnswerAttempt(answer="A", is_correct=False)
                        ],
                        feedback_shown=True,
                        is_complete=True
                    ),
                    Answer(
                        question_id="Q2",
                        current_answer="A",  # Correct answer
                        is_correct=True,
                        attempt_count=1,
                        attempts_history=[
                            AnswerAttempt(answer="A", is_correct=True)
                        ],
                        feedback_shown=True,
                        is_complete=True
                    )
                ],
                created_at=datetime(2024, 1, 15, 8, 0),
                updated_at=datetime(2024, 1, 15, 8, 30)
            ),
            DailyMissionDocument(
                user_id="user123",
                date=date(2024, 1, 16),
                questions=sample_questions,
                status=MissionStatus.ARCHIVED,
                answers=[
                    Answer(
                        question_id="Q1",
                        current_answer="B",  # Correct answer
                        is_correct=True,
                        attempt_count=1,
                        attempts_history=[
                            AnswerAttempt(answer="B", is_correct=True)
                        ],
                        feedback_shown=True,
                        is_complete=True
                    ),
                    Answer(
                        question_id="Q2",
                        current_answer="B",  # Wrong answer
                        is_correct=False,
                        attempt_count=3,
                        attempts_history=[
                            AnswerAttempt(answer="C", is_correct=False),
                            AnswerAttempt(answer="B", is_correct=False),
                            AnswerAttempt(answer="B", is_correct=False)
                        ],
                        feedback_shown=True,
                        is_complete=True
                    )
                ],
                created_at=datetime(2024, 1, 16, 8, 0),
                updated_at=datetime(2024, 1, 16, 8, 30)
            )
        ]
    
    @pytest.mark.asyncio
    async def test_get_user_mistakes_no_mistakes(self, service, mock_mission_repo):
        """Test handling when user has no mistakes"""
        # Mock repository to return empty missions
        mock_mission_repo.find_missions_by_status.return_value = []
        
        result = await service.get_user_mistakes("user123")
        
        assert isinstance(result, ReviewMistakesResponse)
        assert result.total_mistakes == 0
        assert len(result.mistakes) == 0
        assert result.pagination.total_items == 0
        assert result.pagination.total_pages == 0
    
    @pytest.mark.asyncio
    async def test_get_user_mistakes_with_pagination(self, service, mock_mission_repo, sample_missions):
        """Test paginated retrieval of user mistakes"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            [sample_missions[1]]   # ARCHIVED missions
        ]
        
        result = await service.get_user_mistakes(
            user_id="user123",
            page=1,
            items_per_page=1
        )
        
        assert isinstance(result, ReviewMistakesResponse)
        assert result.total_mistakes == 2
        assert len(result.mistakes) == 1  # Limited by page size
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages == 2
        assert result.pagination.has_next is True
        assert result.pagination.has_previous is False
    
    @pytest.mark.asyncio
    async def test_get_user_mistakes_grouped_by_date(self, service, mock_mission_repo, sample_missions):
        """Test grouping mistakes by date"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            [sample_missions[1]]   # ARCHIVED missions
        ]
        
        result = await service.get_user_mistakes(
            user_id="user123",
            page=1,
            items_per_page=10,
            group_by="date"
        )
        
        assert isinstance(result, GroupedReviewMistakesResponse)
        assert result.total_mistakes == 2
        assert len(result.grouped_mistakes) == 2  # Two different dates
        
        # Check date formatting
        expected_dates = ["16 Jan 2024", "15 Jan 2024"]  # Sorted descending
        assert list(result.grouped_mistakes.keys()) == expected_dates
        
        # Check group counts
        assert result.group_counts["16 Jan 2024"] == 1
        assert result.group_counts["15 Jan 2024"] == 1
    
    @pytest.mark.asyncio
    async def test_get_user_mistakes_grouped_by_topic(self, service, mock_mission_repo, sample_missions):
        """Test grouping mistakes by skill area (topic)"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            [sample_missions[1]]   # ARCHIVED missions
        ]
        
        result = await service.get_user_mistakes(
            user_id="user123",
            page=1,
            items_per_page=10,
            group_by="topic"
        )
        
        assert isinstance(result, GroupedReviewMistakesResponse)
        assert result.total_mistakes == 2
        
        # Check topics (alphabetically sorted)
        expected_topics = ["Geography", "Mathematics"]
        assert list(result.grouped_mistakes.keys()) == expected_topics
        
        # Check group counts
        assert result.group_counts["Geography"] == 1
        assert result.group_counts["Mathematics"] == 1
    
    @pytest.mark.asyncio
    async def test_get_user_mistakes_with_skill_area_filter(self, service, mock_mission_repo, sample_missions):
        """Test filtering mistakes by skill area"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            [sample_missions[1]]   # ARCHIVED missions
        ]
        
        result = await service.get_user_mistakes(
            user_id="user123",
            skill_area_filter="Mathematics"
        )
        
        assert isinstance(result, ReviewMistakesResponse)
        assert result.total_mistakes == 1
        assert len(result.mistakes) == 1
        assert result.mistakes[0].skill_area == "Mathematics"
    
    @pytest.mark.asyncio
    async def test_get_available_skill_areas(self, service, mock_mission_repo, sample_missions):
        """Test getting available skill areas"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            [sample_missions[1]]   # ARCHIVED missions
        ]
        
        result = await service.get_available_skill_areas("user123")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "Mathematics" in result
        assert "Geography" in result
        assert result == sorted(result)  # Should be sorted
    
    @pytest.mark.asyncio
    async def test_extract_mistakes_content_validation(self, service, mock_mission_repo, sample_missions):
        """Test that extracted mistake content is correct"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            []  # No archived missions
        ]
        
        result = await service.get_user_mistakes("user123")
        
        assert isinstance(result, ReviewMistakesResponse)
        assert len(result.mistakes) == 1
        
        mistake = result.mistakes[0]
        assert mistake.question_id == "Q1"
        assert mistake.question_text == "What is 2+2?"
        assert mistake.skill_area == "Mathematics"
        assert mistake.difficulty_level == 1
        assert mistake.user_answer_id == "A"
        assert mistake.user_answer_text == "3"
        assert mistake.correct_answer_id == "B"
        assert mistake.correct_answer_text == "4"
        assert mistake.explanation == "The correct answer is 4."
        assert mistake.attempt_count == 2
        assert mistake.mission_date == date(2024, 1, 15)
    
    @pytest.mark.asyncio
    async def test_pagination_edge_cases(self, service, mock_mission_repo, sample_missions):
        """Test pagination edge cases"""
        # Mock repository calls
        mock_mission_repo.find_missions_by_status.side_effect = [
            [sample_missions[0]],  # COMPLETE missions
            [sample_missions[1]]   # ARCHIVED missions
        ]
        
        # Test last page
        result = await service.get_user_mistakes(
            user_id="user123",
            page=2,
            items_per_page=1
        )
        
        assert isinstance(result, ReviewMistakesResponse)
        assert result.pagination.current_page == 2
        assert result.pagination.has_next is False
        assert result.pagination.has_previous is True
        assert len(result.mistakes) == 1
    
    def test_get_choice_text_helper(self, service):
        """Test the helper method for getting choice text"""
        choices = [
            ChoiceOption(id="A", text="Option A"),
            ChoiceOption(id="B", text="Option B")
        ]
        
        assert service._get_choice_text(choices, "A") == "Option A"
        assert service._get_choice_text(choices, "B") == "Option B"
        assert service._get_choice_text(choices, "C") == "Unknown"
    
    @pytest.mark.asyncio
    async def test_empty_missions_handling(self, service, mock_mission_repo):
        """Test handling of missions with no answers"""
        empty_mission = DailyMissionDocument(
            user_id="user123",
            date=date(2024, 1, 15),
            questions=[],
            status=MissionStatus.COMPLETE,
            answers=[],
            created_at=datetime(2024, 1, 15, 8, 0),
            updated_at=datetime(2024, 1, 15, 8, 30)
        )
        
        mock_mission_repo.find_missions_by_status.side_effect = [
            [empty_mission],  # COMPLETE missions
            []  # ARCHIVED missions
        ]
        
        result = await service.get_user_mistakes("user123")
        
        assert isinstance(result, ReviewMistakesResponse)
        assert result.total_mistakes == 0
        assert len(result.mistakes) == 0 