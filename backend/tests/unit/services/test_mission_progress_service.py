import pytest
from datetime import datetime, date
from unittest.mock import AsyncMock

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question, Answer, AnswerAttempt
from backend.services.mission_progress_service import (
    update_mission_progress,
    submit_answer_with_feedback,
    mark_feedback_shown,
    reset_question_for_retry,
    _is_answer_correct,
    _is_mission_complete
)
from backend.services.utils import TARGET_TIMEZONE

# Mock MissionRepository for testing
@pytest.fixture
def mock_mission_repo():
    return AsyncMock()

# Sample question for testing
@pytest.fixture
def sample_question():
    return Question(
        question_id="q1",
        question_text="What is 2+2?",
        skill_area="math",
        difficulty_level=1,
        choices=[
            {"id": "a", "text": "3"},
            {"id": "b", "text": "4"},
            {"id": "c", "text": "5"}
        ],
        correct_answer_id="b",
        feedback_th="2+2 = 4 เป็นการบวกพื้นฐาน"
    )

@pytest.fixture
def sample_mission(sample_question):
    return DailyMissionDocument(
        user_id="test_user",
        date=datetime.now(TARGET_TIMEZONE).date(),
        questions=[sample_question],
        status=MissionStatus.IN_PROGRESS,
        current_question_index=0,
        answers=[]
    )

# Test helper functions
def test_is_answer_correct():
    """Test the answer correctness checking function."""
    assert _is_answer_correct("b", "b") == True
    assert _is_answer_correct("B", "b") == True
    assert _is_answer_correct(" b ", "b") == True
    assert _is_answer_correct("a", "b") == False
    assert _is_answer_correct("", "b") == False

def test_is_mission_complete_empty():
    """Test mission completion with no answers."""
    mission = DailyMissionDocument(
        user_id="test",
        date=date.today(),
        questions=[Question(question_id="q1", question_text="Q1?", skill_area="test", difficulty_level=1, choices=[], correct_answer_id="a", feedback_th="feedback")],
        answers=[]
    )
    assert _is_mission_complete(mission) == False

def test_is_mission_complete_partial():
    """Test mission completion with partial answers."""
    mission = DailyMissionDocument(
        user_id="test",
        date=date.today(),
        questions=[
            Question(question_id="q1", question_text="Q1?", skill_area="test", difficulty_level=1, choices=[], correct_answer_id="a", feedback_th="feedback"),
            Question(question_id="q2", question_text="Q2?", skill_area="test", difficulty_level=1, choices=[], correct_answer_id="b", feedback_th="feedback")
        ],
        answers=[
            Answer(question_id="q1", current_answer="a", is_complete=True, feedback_shown=True)
        ]
    )
    assert _is_mission_complete(mission) == False

def test_is_mission_complete_all_complete():
    """Test mission completion with all questions completed and feedback shown."""
    mission = DailyMissionDocument(
        user_id="test",
        date=date.today(),
        questions=[
            Question(question_id="q1", question_text="Q1?", skill_area="test", difficulty_level=1, choices=[], correct_answer_id="a", feedback_th="feedback"),
            Question(question_id="q2", question_text="Q2?", skill_area="test", difficulty_level=1, choices=[], correct_answer_id="b", feedback_th="feedback")
        ],
        answers=[
            Answer(question_id="q1", current_answer="a", is_complete=True, feedback_shown=True),
            Answer(question_id="q2", current_answer="b", is_complete=True, feedback_shown=True)
        ]
    )
    assert _is_mission_complete(mission) == True

def test_is_mission_complete_no_feedback():
    """Test mission completion when answers are complete but feedback not shown."""
    mission = DailyMissionDocument(
        user_id="test",
        date=date.today(),
        questions=[
            Question(question_id="q1", question_text="Q1?", skill_area="test", difficulty_level=1, choices=[], correct_answer_id="a", feedback_th="feedback")
        ],
        answers=[
            Answer(question_id="q1", current_answer="a", is_complete=True, feedback_shown=False)
        ]
    )
    assert _is_mission_complete(mission) == False

# Test answer submission with feedback
@pytest.mark.asyncio
async def test_submit_answer_correct_first_try(mock_mission_repo, sample_mission, sample_question):
    """Test submitting a correct answer on first try."""
    mock_mission_repo.find_mission.return_value = sample_mission
    
    feedback = await submit_answer_with_feedback(
        user_id="test_user",
        question_id="q1",
        user_answer="b",
        mission_repo=mock_mission_repo
    )
    
    assert feedback["already_complete"] == False
    assert feedback["is_correct"] == True
    assert feedback["correct_answer"] == "b"
    assert feedback["explanation"] == "2+2 = 4 เป็นการบวกพื้นฐาน"
    assert feedback["attempt_count"] == 1
    assert feedback["can_retry"] == False  # Correct answer, no retry needed
    assert feedback["question_complete"] == True
    
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_submit_answer_incorrect_first_try(mock_mission_repo, sample_mission, sample_question):
    """Test submitting an incorrect answer on first try."""
    mock_mission_repo.find_mission.return_value = sample_mission
    
    feedback = await submit_answer_with_feedback(
        user_id="test_user",
        question_id="q1",
        user_answer="a",
        mission_repo=mock_mission_repo
    )
    
    assert feedback["already_complete"] == False
    assert feedback["is_correct"] == False
    assert feedback["correct_answer"] == "b"
    assert feedback["attempt_count"] == 1
    assert feedback["can_retry"] == True
    assert feedback["question_complete"] == False
    
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_submit_answer_max_retries_reached(mock_mission_repo, sample_mission, sample_question):
    """Test submitting answer when max retries reached."""
    # Pre-fill mission with existing attempts
    existing_answer = Answer(
        question_id="q1",
        current_answer="a",
        is_correct=False,
        attempt_count=2,
        attempts_history=[
            AnswerAttempt(answer="a", is_correct=False),
            AnswerAttempt(answer="c", is_correct=False)
        ],
        feedback_shown=True,
        is_complete=False,
        max_retries=3
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    feedback = await submit_answer_with_feedback(
        user_id="test_user",
        question_id="q1",
        user_answer="a",  # Still incorrect
        mission_repo=mock_mission_repo
    )
    
    assert feedback["already_complete"] == False
    assert feedback["is_correct"] == False
    assert feedback["attempt_count"] == 3
    assert feedback["can_retry"] == False  # Max retries reached
    assert feedback["question_complete"] == True  # Complete due to max retries
    
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_submit_answer_already_complete(mock_mission_repo, sample_mission, sample_question):
    """Test submitting answer for already completed question."""
    # Pre-fill mission with completed answer
    existing_answer = Answer(
        question_id="q1",
        current_answer="b",
        is_correct=True,
        attempt_count=1,
        is_complete=True,
        feedback_shown=True
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    feedback = await submit_answer_with_feedback(
        user_id="test_user",
        question_id="q1",
        user_answer="b",
        mission_repo=mock_mission_repo
    )
    
    assert feedback["already_complete"] == True
    assert feedback["is_correct"] == True
    assert feedback["attempt_count"] == 1
    
    # Should not save mission again
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_submit_answer_question_not_found(mock_mission_repo, sample_mission):
    """Test submitting answer for non-existent question."""
    mock_mission_repo.find_mission.return_value = sample_mission
    
    with pytest.raises(ValueError, match="Question nonexistent not found in mission"):
        await submit_answer_with_feedback(
            user_id="test_user",
            question_id="nonexistent",
            user_answer="a",
            mission_repo=mock_mission_repo
        )

@pytest.mark.asyncio
async def test_submit_answer_no_mission(mock_mission_repo):
    """Test submitting answer when no mission exists."""
    mock_mission_repo.find_mission.return_value = None
    
    with pytest.raises(ValueError, match="No active mission found for user"):
        await submit_answer_with_feedback(
            user_id="test_user",
            question_id="q1",
            user_answer="a",
            mission_repo=mock_mission_repo
        )

# Test feedback marking
@pytest.mark.asyncio
async def test_mark_feedback_shown(mock_mission_repo, sample_mission):
    """Test marking feedback as shown."""
    existing_answer = Answer(
        question_id="q1",
        current_answer="b",
        is_correct=True,
        feedback_shown=False,
        is_complete=True
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    result = await mark_feedback_shown(
        user_id="test_user",
        question_id="q1",
        mission_repo=mock_mission_repo
    )
    
    assert result is not None
    assert existing_answer.feedback_shown == True
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_mark_feedback_shown_completes_mission(mock_mission_repo, sample_mission):
    """Test that marking feedback shown can complete the mission."""
    existing_answer = Answer(
        question_id="q1",
        current_answer="b",
        is_correct=True,
        feedback_shown=False,
        is_complete=True
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    result = await mark_feedback_shown(
        user_id="test_user",
        question_id="q1",
        mission_repo=mock_mission_repo
    )
    
    assert result.status == MissionStatus.COMPLETE
    mock_mission_repo.save_mission.assert_called_once()

# Test question retry
@pytest.mark.asyncio
async def test_reset_question_for_retry(mock_mission_repo, sample_mission):
    """Test resetting a question for retry."""
    existing_answer = Answer(
        question_id="q1",
        current_answer="a",
        is_correct=False,
        attempt_count=1,
        feedback_shown=True,
        is_complete=False,
        max_retries=3
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    result = await reset_question_for_retry(
        user_id="test_user",
        question_id="q1",
        mission_repo=mock_mission_repo
    )
    
    assert result["success"] == True
    assert result["remaining_attempts"] == 2
    assert existing_answer.current_answer == ""
    assert existing_answer.feedback_shown == False
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_reset_question_already_complete(mock_mission_repo, sample_mission):
    """Test resetting a question that's already complete."""
    existing_answer = Answer(
        question_id="q1",
        current_answer="b",
        is_correct=True,
        is_complete=True
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    result = await reset_question_for_retry(
        user_id="test_user",
        question_id="q1",
        mission_repo=mock_mission_repo
    )
    
    assert result["success"] == False
    assert result["error"] == "Question already completed"

@pytest.mark.asyncio
async def test_reset_question_max_retries_exceeded(mock_mission_repo, sample_mission):
    """Test resetting a question when max retries exceeded."""
    existing_answer = Answer(
        question_id="q1",
        current_answer="a",
        attempt_count=3,
        max_retries=3,
        is_complete=False
    )
    sample_mission.answers = [existing_answer]
    mock_mission_repo.find_mission.return_value = sample_mission
    
    result = await reset_question_for_retry(
        user_id="test_user",
        question_id="q1",
        mission_repo=mock_mission_repo
    )
    
    assert result["success"] == False
    assert result["error"] == "Maximum retries exceeded"

# Legacy compatibility tests
@pytest.mark.asyncio
async def test_update_mission_progress_legacy_compatibility(mock_mission_repo):
    """Test that the legacy update_mission_progress function still works."""
    user_id = "test_user"
    today = datetime.now(TARGET_TIMEZONE).date()
    questions = [Question(question_id="q1", question_text="Q1?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="a", feedback_th="fb")]
    mission_doc = DailyMissionDocument(user_id=user_id, date=today, questions=questions, status=MissionStatus.IN_PROGRESS, current_question_index=0)
    mock_mission_repo.find_mission.return_value = mission_doc

    # Legacy format answers
    legacy_answers = [{"question_id": "q1", "answer": "a", "feedback_shown": True}]
    updated_mission = await update_mission_progress(user_id, 1, legacy_answers, mock_mission_repo)

    assert updated_mission is not None
    assert updated_mission.current_question_index == 1
    assert len(updated_mission.answers) == 1
    assert updated_mission.answers[0].question_id == "q1"
    assert updated_mission.answers[0].current_answer == "a"
    assert updated_mission.answers[0].feedback_shown == True
    mock_mission_repo.save_mission.assert_called_once() 