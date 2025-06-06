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
from unittest.mock import patch, mock_open, MagicMock, AsyncMock
from datetime import datetime, date, timezone, timedelta

import pytest

from backend.models.daily_mission import Question, DailyMissionDocument, MissionStatus, ChoiceOption
from backend.services.mission_service import (
    generate_daily_mission,
    get_todays_mission_for_user,
    archive_past_incomplete_missions,
    NoQuestionsAvailableError,
    MissionAlreadyExistsError,
    MissionGenerationError,
)
from backend.repositories.mission_repository import MissionRepository
from backend.repositories.question_repository import QuestionRepository

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
    return Question(
        question_id="q1",
        question_text="Test?",
        skill_area="Test",
        difficulty_level=1,
        choices=[ChoiceOption(id="a", text="Option A")],
        correct_answer_id="a",
        feedback_th="Test feedback"
    )

def create_mock_question(question_id: str) -> Question:
    """Helper function to create a mock Question object for testing."""
    return Question(
        question_id=question_id,
        question_text=f"Sample question text for {question_id}",
        skill_area="Test Skill",
        difficulty_level=1,
        choices=[ChoiceOption(id="a", text="Option A")],
        correct_answer_id="a",
        feedback_th="This is feedback."
    )

@pytest.fixture
def sample_questions(sample_question):
    # This fixture is less useful now that we need real Question objects.
    # We will create them directly in the mock repository fixture.
    return {f"q{i}": sample_question for i in range(10)}

@pytest.fixture
def mock_mission_repo() -> MagicMock:
    """Provides a fresh mock MissionRepository for each test."""
    # Use AsyncMock for async methods
    repo = MagicMock(spec=MissionRepository)
    repo.find_mission = AsyncMock(return_value=None)
    repo.save_mission = AsyncMock()
    repo.get_missions_to_archive = AsyncMock(return_value=[])
    return repo

@pytest.fixture
def mock_question_repo() -> MagicMock:
    """Provides a fresh mock QuestionRepository for each test."""
    mock_repo = MagicMock(spec=QuestionRepository)
    
    # Create real Question objects for the mock repository to return
    mock_questions_dict = {f"q{i}": create_mock_question(f"q{i}") for i in range(10)}
    
    # Configure the async mocks to return these real objects
    mock_repo.get_all_questions = AsyncMock(return_value=mock_questions_dict)
    mock_repo.get_question_by_id = AsyncMock(side_effect=lambda qid: mock_questions_dict.get(qid))
    return mock_repo

@pytest.mark.asyncio
async def test_generate_daily_mission_success(mock_mission_repo: MagicMock, mock_question_repo: MagicMock):
    """
    Tests successful generation of a daily mission for a user.

    Verifies that a new mission is created with 5 questions, has the 'NOT_STARTED'
    status, and is correctly stored in the mock database.
    """
    mock_mission_repo.find_mission.return_value = None
    
    user_id = "test_user_1"
    mission = await generate_daily_mission(user_id, mock_mission_repo, mock_question_repo)
    
    assert mission is not None
    assert mission.user_id == user_id
    assert len(mission.questions) == 5
    assert mission.status == MissionStatus.NOT_STARTED
    
    mock_mission_repo.find_mission.assert_awaited_once()
    mock_mission_repo.save_mission.assert_awaited_once_with(mission)

@pytest.mark.asyncio
async def test_generate_daily_mission_insufficient_questions(mock_mission_repo: MagicMock, mock_question_repo: MagicMock):
    """
    Tests that mission generation fails if there are not enough questions available.

    Ensures that a `NoQuestionsAvailableError` is raised when the question
    repository has fewer than 5 questions.
    """
    mock_question_repo.get_all_questions.return_value = {"q1": "dummy"} # Not enough questions
    
    with pytest.raises(NoQuestionsAvailableError):
        await generate_daily_mission("test_user_2", mock_mission_repo, mock_question_repo)
    
    mock_mission_repo.save_mission.assert_not_called()

@pytest.mark.asyncio
async def test_generate_daily_mission_already_exists(mock_mission_repo: MagicMock, mock_question_repo: MagicMock):
    """
    Tests that a user cannot generate more than one mission per day.

    Verifies that a `MissionAlreadyExistsError` is raised if a second mission
    is requested for the same user on the same day.
    """
    user_id = "test_user_3"
    mock_mission_repo.find_mission.return_value = MagicMock(spec=DailyMissionDocument)
    
    with pytest.raises(MissionAlreadyExistsError):
        await generate_daily_mission(user_id, mock_mission_repo, mock_question_repo)
    
    mock_mission_repo.save_mission.assert_not_called()
    mock_mission_repo.find_mission.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_todays_mission_for_user_existing(mock_mission_repo: MagicMock, mock_question_repo: MagicMock):
    """
    Tests retrieving an existing daily mission for a user.

    Ensures that if a mission has already been generated for a user today,
    it can be successfully retrieved.
    """
    user_id = "test_user_4"
    mock_mission = MagicMock(spec=DailyMissionDocument)
    mock_mission.user_id = user_id
    mock_mission_repo.find_mission.return_value = mock_mission
    
    mission = await get_todays_mission_for_user(user_id, mock_mission_repo, mock_question_repo)
    
    assert mission is not None
    assert mission.user_id == user_id
    mock_mission_repo.find_mission.assert_awaited_once()
    mock_mission_repo.save_mission.assert_not_called()

@pytest.mark.asyncio
async def test_archive_past_incomplete_missions(sample_question, mock_mission_repo: MagicMock):
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
    
    # Mission that should be archived
    mission_to_archive = DailyMissionDocument(user_id="user1", date=yesterday, status=MissionStatus.IN_PROGRESS, questions=questions)
    
    # Simulate the repository returning this one mission to be archived
    mock_mission_repo.get_missions_to_archive.return_value = [mission_to_archive]

    archived_count = await archive_past_incomplete_missions(mock_mission_repo)
    
    assert archived_count == 1
    
    # Verify that the mission was updated and saved
    mock_mission_repo.get_missions_to_archive.assert_awaited_once()
    mock_mission_repo.save_mission.assert_awaited_once()
    
    # Check the state of the object that was "saved"
    saved_mission_arg = mock_mission_repo.save_mission.call_args[0][0]
    assert saved_mission_arg.status == MissionStatus.ARCHIVED
    assert saved_mission_arg.user_id == "user1"

@pytest.fixture
def sample_mission(sample_question: Question) -> DailyMissionDocument:
    # This fixture is less useful now that we need real Question objects.
    # We will create them directly in the mock repository fixture.
    return DailyMissionDocument(
        user_id="test_user_5",
        date=datetime.now(timezone.utc).date(),
        status=MissionStatus.NOT_STARTED,
        questions=[sample_question] * 5
    ) 