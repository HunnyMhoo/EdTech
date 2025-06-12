import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime
import json

from backend.models.daily_mission import (
    DailyMissionDocument, 
    MissionStatus, 
    Question, 
    ChoiceOption, 
    Answer,
    AnswerAttempt
)


class TestReviewMistakesIntegration:
    """Integration tests for review mistakes functionality"""
    
    @pytest.fixture
    async def sample_mission_with_mistakes(self, mission_repo):
        """Create a sample mission with mistakes for testing"""
        mission = DailyMissionDocument(
            user_id="test_user_123",
            date=date(2024, 1, 15),
            questions=[
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
            ],
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
        )
        
        await mission_repo.save_mission(mission)
        return mission
    
    @pytest.fixture
    async def sample_archived_mission_with_mistakes(self, mission_repo):
        """Create an archived mission with mistakes for testing"""
        mission = DailyMissionDocument(
            user_id="test_user_123",
            date=date(2024, 1, 16),
            questions=[
                Question(
                    question_id="Q3",
                    question_text="What is 5-3?",
                    skill_area="Mathematics",
                    difficulty_level=1,
                    choices=[
                        ChoiceOption(id="A", text="1"),
                        ChoiceOption(id="B", text="2"),
                        ChoiceOption(id="C", text="3")
                    ],
                    correct_answer_id="B",
                    feedback_th="5 minus 3 equals 2."
                )
            ],
            status=MissionStatus.ARCHIVED,
            answers=[
                Answer(
                    question_id="Q3",
                    current_answer="C",  # Wrong answer
                    is_correct=False,
                    attempt_count=1,
                    attempts_history=[
                        AnswerAttempt(answer="C", is_correct=False)
                    ],
                    feedback_shown=True,
                    is_complete=True
                )
            ],
            created_at=datetime(2024, 1, 16, 8, 0),
            updated_at=datetime(2024, 1, 16, 8, 30)
        )
        
        await mission_repo.save_mission(mission)
        return mission
    
        async def test_get_review_mistakes_success(
        self,
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test successful retrieval of review mistakes"""
        import httpx
        response = httpx.get(
            "http://127.0.0.1:8000/api/review-mistakes/test_user_123"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["total_mistakes"] == 2
        assert len(data["data"]["mistakes"]) == 2
        
        # Check pagination info
        pagination = data["data"]["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["total_items"] == 2
        assert pagination["has_next"] is False
        assert pagination["has_previous"] is False
        
        # Verify mistake content
        mistakes = data["data"]["mistakes"]
        math_mistake = next(m for m in mistakes if m["skill_area"] == "Mathematics")
        assert math_mistake["question_text"] in ["What is 2+2?", "What is 5-3?"]
        assert math_mistake["user_answer_text"] in ["3", "3"]  # Both wrong answers are "3"
        assert math_mistake["correct_answer_text"] in ["4", "2"]
        assert not math_mistake["user_answer_id"] == math_mistake["correct_answer_id"]
    
    async def test_get_review_mistakes_pagination(
        self, 
        client: TestClient, 
        auth_headers, 
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test pagination functionality"""
        # Get first page with 1 item per page
        response = client.get(
            "/api/review-mistakes/?page=1&items_per_page=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["total_mistakes"] == 2
        assert len(data["data"]["mistakes"]) == 1
        assert data["data"]["pagination"]["current_page"] == 1
        assert data["data"]["pagination"]["total_pages"] == 2
        assert data["data"]["pagination"]["has_next"] is True
        assert data["data"]["pagination"]["has_previous"] is False
        
        # Get second page
        response = client.get(
            "/api/review-mistakes/?page=2&items_per_page=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]["mistakes"]) == 1
        assert data["data"]["pagination"]["current_page"] == 2
        assert data["data"]["pagination"]["has_next"] is False
        assert data["data"]["pagination"]["has_previous"] is True
    
    async def test_get_grouped_review_mistakes_by_date(
        self, 
        client: TestClient, 
        auth_headers, 
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test grouped mistakes by date"""
        response = client.get(
            "/api/review-mistakes/grouped?group_by=date",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["data"]["total_mistakes"] == 2
        
        grouped_mistakes = data["data"]["grouped_mistakes"]
        assert len(grouped_mistakes) == 2  # Two different dates
        
        # Check date formatting (DD MMM YYYY)
        dates = list(grouped_mistakes.keys())
        assert any("Jan 2024" in date for date in dates)
        
        # Check group counts
        group_counts = data["data"]["group_counts"]
        assert sum(group_counts.values()) == 2
    
    async def test_get_grouped_review_mistakes_by_topic(
        self, 
        client: TestClient, 
        auth_headers, 
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test grouped mistakes by topic (skill area)"""
        response = client.get(
            "/api/review-mistakes/grouped?group_by=topic",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["data"]["total_mistakes"] == 2
        
        grouped_mistakes = data["data"]["grouped_mistakes"]
        assert "Mathematics" in grouped_mistakes
        
        # Should have 2 mathematics mistakes (from both missions)
        group_counts = data["data"]["group_counts"]
        assert group_counts["Mathematics"] == 2
    
    async def test_get_review_mistakes_with_skill_area_filter(
        self, 
        client: TestClient, 
        auth_headers, 
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test filtering mistakes by skill area"""
        response = client.get(
            "/api/review-mistakes/?skill_area=Mathematics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["total_mistakes"] == 2  # Both mistakes are in Mathematics
        mistakes = data["data"]["mistakes"]
        
        for mistake in mistakes:
            assert mistake["skill_area"] == "Mathematics"
    
    async def test_get_available_skill_areas(
        self, 
        client: TestClient, 
        auth_headers, 
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test getting available skill areas"""
        response = client.get(
            "/api/review-mistakes/skill-areas",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        skill_areas = data["data"]
        assert isinstance(skill_areas, list)
        assert "Mathematics" in skill_areas
        assert len(skill_areas) >= 1  # At least Mathematics
    
    async def test_get_review_stats(
        self, 
        client: TestClient, 
        auth_headers, 
        sample_mission_with_mistakes,
        sample_archived_mission_with_mistakes
    ):
        """Test getting review statistics"""
        response = client.get(
            "/api/review-mistakes/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        stats = data["data"]
        
        assert stats["total_mistakes"] == 2
        assert stats["skill_areas_count"] >= 1
        assert "Mathematics" in stats["skill_areas"]
        assert "difficulty_breakdown" in stats
        assert isinstance(stats["difficulty_breakdown"], dict)
    
    async def test_get_review_mistakes_no_mistakes(
        self, 
        client: TestClient, 
        auth_headers_different_user
    ):
        """Test response when user has no mistakes"""
        response = client.get(
            "/api/review-mistakes/",
            headers=auth_headers_different_user
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["message"] == "Great job! You have no mistakes to review right now."
        assert data["data"]["total_mistakes"] == 0
        assert len(data["data"]["mistakes"]) == 0
    
    async def test_get_review_mistakes_unauthorized(self, client: TestClient):
        """Test unauthorized access"""
        response = client.get("/api/review-mistakes/")
        
        assert response.status_code == 401
    
    async def test_get_grouped_mistakes_invalid_group_by(
        self, 
        client: TestClient, 
        auth_headers
    ):
        """Test invalid group_by parameter"""
        response = client.get(
            "/api/review-mistakes/grouped?group_by=invalid",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_pagination_out_of_range(
        self, 
        client: TestClient, 
        auth_headers,
        sample_mission_with_mistakes
    ):
        """Test pagination with page number out of range"""
        response = client.get(
            "/api/review-mistakes/?page=999&items_per_page=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty results but not error
        assert len(data["data"]["mistakes"]) == 0
        assert data["data"]["pagination"]["current_page"] == 999
    
    async def test_performance_large_dataset(
        self, 
        client: TestClient, 
        auth_headers,
        sample_mission_with_mistakes
    ):
        """Test performance with reasonable dataset"""
        import time
        
        start_time = time.time()
        response = client.get(
            "/api/review-mistakes/?items_per_page=50",
            headers=auth_headers
        )
        end_time = time.time()
        
        assert response.status_code == 200
        # Should respond within 300ms as per requirements
        assert (end_time - start_time) < 0.3  # 300ms 