"""
Unit tests for the mission_service module.

This test suite covers the functionality of generating, retrieving, and managing
daily missions for users. It ensures that mission creation, error handling, and
archiving processes work as expected.
"""
import asyncio
import csv
from io import StringIO
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, date, timezone, timedelta

import pytest

from backend.models.daily_mission import Question, DailyMissionDocument, MissionStatus
from backend.services.mission_service import (
    generate_daily_mission,
    get_todays_mission_for_user,
    archive_past_incomplete_missions,
    NoQuestionsAvailableError,
    MissionAlreadyExistsError,
    _mock_db_missions,
    MissionGenerationError
)

# Helper to create CSV content string
def create_csv_content(headers, rows):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()

@pytest.fixture
def mock_csv_file_path():
    # This path is nominal and used in messages; `open` is mocked directly.
    return Path("mock_questions.csv")

# Fixture to provide a sample question
@pytest.fixture
def sample_question():
    return Question(question_id="q1", question_text="Test?", skill_area="Test", difficulty_level=1, feedback_th="Test feedback")

# Fixture to provide a list of sample questions
@pytest.fixture
def sample_questions(sample_question):
    return {f"q{i}": sample_question for i in range(10)}

@pytest.fixture(autouse=True)
def clear_mock_db():
    _mock_db_missions.clear()
    yield

@pytest.mark.asyncio
async def test_generate_daily_mission_success(sample_questions):
    """
    Tests successful generation of a daily mission for a user.

    Verifies that a new mission is created with 5 questions, has the 'NOT_STARTED'
    status, and is correctly stored in the mock database.
    """
    with patch('backend.services.mission_service.question_repository') as mock_repo:
        mock_repo.get_all_questions.return_value = sample_questions
        mock_repo.get_question_by_id.side_effect = lambda qid: sample_questions.get(qid)
        
        user_id = "test_user_1"
        mission = await generate_daily_mission(user_id)
        
        assert mission is not None
        assert mission.user_id == user_id
        assert len(mission.questions) == 5
        assert mission.status == MissionStatus.NOT_STARTED
        assert len(_mock_db_missions) == 1

@pytest.mark.asyncio
async def test_generate_daily_mission_insufficient_questions():
    """
    Tests that mission generation fails if there are not enough questions available.

    Ensures that a `NoQuestionsAvailableError` is raised when the question
    repository has fewer than 5 questions.
    """
    with patch('backend.services.mission_service.question_repository') as mock_repo:
        mock_repo.get_all_questions.return_value = {"q1": "dummy"} # Not enough questions
        
        with pytest.raises(NoQuestionsAvailableError):
            await generate_daily_mission("test_user_2")

@pytest.mark.asyncio
async def test_generate_daily_mission_already_exists(sample_questions):
    """
    Tests that a user cannot generate more than one mission per day.

    Verifies that a `MissionAlreadyExistsError` is raised if a second mission
    is requested for the same user on the same day.
    """
    with patch('backend.services.mission_service.question_repository') as mock_repo:
        mock_repo.get_all_questions.return_value = sample_questions
        mock_repo.get_question_by_id.side_effect = lambda qid: sample_questions.get(qid)
        
        user_id = "test_user_3"
        await generate_daily_mission(user_id) # First mission
        
        with pytest.raises(MissionAlreadyExistsError):
            await generate_daily_mission(user_id) # Second mission on same day

@pytest.mark.asyncio
async def test_get_todays_mission_for_user_existing(sample_questions):
    """
    Tests retrieving an existing daily mission for a user.

    Ensures that if a mission has already been generated for a user today,
    it can be successfully retrieved.
    """
    user_id = "test_user_4"
    with patch('backend.services.mission_service.question_repository') as mock_repo:
        mock_repo.get_all_questions.return_value = sample_questions
        mock_repo.get_question_by_id.side_effect = lambda qid: sample_questions.get(qid)
        
        await generate_daily_mission(user_id)
    
    mission = await get_todays_mission_for_user(user_id)
    assert mission is not None
    assert mission.user_id == user_id

@pytest.mark.asyncio
async def test_archive_past_incomplete_missions(sample_question):
    """
    Tests the archiving of past-due, incomplete missions.

    Verifies that missions from previous days with a status of 'IN_PROGRESS'
    are correctly updated to 'ARCHIVED', while completed and current-day
    missions are left unchanged.
    """
    # Setup: Create missions with different dates and statuses
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    
    questions = [sample_question] * 5
    
    _mock_db_missions.extend([
        DailyMissionDocument(user_id="user1", date=yesterday, status=MissionStatus.IN_PROGRESS, questions=questions),
        DailyMissionDocument(user_id="user2", date=yesterday, status=MissionStatus.COMPLETE, questions=questions),
        DailyMissionDocument(user_id="user3", date=today, status=MissionStatus.IN_PROGRESS, questions=questions),
    ])
    
    archived_count = await archive_past_incomplete_missions()
    
    assert archived_count == 1
    
    archived_mission = next(m for m in _mock_db_missions if m.user_id == "user1")
    completed_mission = next(m for m in _mock_db_missions if m.user_id == "user2")
    current_mission = next(m for m in _mock_db_missions if m.user_id == "user3")

    assert archived_mission.status == MissionStatus.ARCHIVED
    assert completed_mission.status == MissionStatus.COMPLETE # Should not be changed
    assert current_mission.status == MissionStatus.IN_PROGRESS # Should not be changed 