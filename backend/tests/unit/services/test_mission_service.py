import pytest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question

# Import directly from the new service files to bypass the old mission_service.py
from backend.services.mission_generation_service import (
    generate_daily_mission,
    NoQuestionsAvailableError,
    MissionAlreadyExistsError,
)
from backend.services.mission_service import get_todays_mission_for_user
from backend.services.mission_progress_service import update_mission_progress
from backend.services.mission_lifecycle_service import archive_past_incomplete_missions

TARGET_TIMEZONE = timezone(timedelta(hours=7))

@pytest.fixture
def mock_question_repo():
    repo = AsyncMock()
    repo.get_all_questions.return_value = {
        f"q{i}": Question(question_id=f"q{i}", question_text=f"Q{i}?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="c1", feedback_th="fb")
        for i in range(10)
    }
    repo.get_question_by_id.side_effect = lambda qid: Question(question_id=qid, question_text=f"{qid}?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="c1", feedback_th="fb")
    return repo

@pytest.fixture
def mock_mission_repo():
    repo = AsyncMock()
    repo.find_mission.return_value = None
    repo.save_mission.return_value = None
    repo.get_missions_to_archive.return_value = []
    return repo

@pytest.mark.asyncio
async def test_generate_daily_mission_success(mock_mission_repo, mock_question_repo):
    user_id = "test_user"
    mission = await generate_daily_mission(user_id, mock_mission_repo, mock_question_repo)
    
    assert isinstance(mission, DailyMissionDocument)
    assert mission.user_id == user_id
    assert len(mission.questions) == 5
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_generate_daily_mission_no_questions(mock_mission_repo, mock_question_repo):
    mock_question_repo.get_all_questions.return_value = {}
    with pytest.raises(NoQuestionsAvailableError):
        await generate_daily_mission("user1", mock_mission_repo, mock_question_repo)

@pytest.mark.asyncio
async def test_generate_daily_mission_already_exists(mock_mission_repo, mock_question_repo):
    mock_mission_repo.find_mission.return_value = "existing_mission"
    with pytest.raises(MissionAlreadyExistsError):
        await generate_daily_mission("user1", mock_mission_repo, mock_question_repo)

@pytest.mark.asyncio
async def test_get_todays_mission_for_user_exists(mock_mission_repo, mock_question_repo):
    user_id = "user_exists"
    today = datetime.now(TARGET_TIMEZONE).date()
    mission_doc = DailyMissionDocument(user_id=user_id, date=today, questions=[], status=MissionStatus.NOT_STARTED)
    mock_mission_repo.find_mission.return_value = mission_doc

    result = await get_todays_mission_for_user(user_id, mock_mission_repo, mock_question_repo)
    
    assert result == mission_doc
    mock_mission_repo.find_mission.assert_called_once()
    # Ensure generate was NOT called
    mock_mission_repo.save_mission.assert_not_called()

@pytest.mark.asyncio
async def test_get_todays_mission_for_user_generates_new(mock_mission_repo, mock_question_repo):
    user_id = "new_user"
    mock_mission_repo.find_mission.return_value = None # No mission exists

    result = await get_todays_mission_for_user(user_id, mock_mission_repo, mock_question_repo)
    
    assert result is not None
    assert result.user_id == user_id
    # find_mission is called twice: once in get_todays_mission, once in generate_daily_mission
    assert mock_mission_repo.find_mission.call_count == 2
    mock_mission_repo.save_mission.assert_called_once() # A new mission was saved

@pytest.mark.asyncio
async def test_update_mission_progress_success(mock_mission_repo):
    user_id = "progress_user"
    today = datetime.now(TARGET_TIMEZONE).date()
    # Mission has 5 questions, but only 1 answer is provided.
    questions = [Question(question_id=f"q{i}", question_text=f"Q{i}?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="c1", feedback_th="fb") for i in range(5)]
    mission_doc = DailyMissionDocument(user_id=user_id, date=today, questions=questions, status=MissionStatus.IN_PROGRESS, current_question_index=0)
    mock_mission_repo.find_mission.return_value = mission_doc

    # Provide one answer
    answers = [{"question_id": "q0", "answer": "a", "feedback_shown": True}]
    updated_mission = await update_mission_progress(user_id, 1, answers, mock_mission_repo)

    assert updated_mission is not None
    assert updated_mission.current_question_index == 1
    # The mission is still IN_PROGRESS because not all questions are answered.
    assert updated_mission.status == MissionStatus.IN_PROGRESS
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_update_mission_progress_completion(mock_mission_repo):
    user_id = "completion_user"
    today = datetime.now(TARGET_TIMEZONE).date()
    questions = [Question(question_id=f"q{i}", question_text=f"Q{i}?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="c1", feedback_th="fb") for i in range(2)]
    mission_doc = DailyMissionDocument(user_id=user_id, date=today, questions=questions, status=MissionStatus.IN_PROGRESS)
    mock_mission_repo.find_mission.return_value = mission_doc

    # Provide answers for all questions with feedback shown
    answers = [
        {"question_id": "q0", "answer": "a", "feedback_shown": True},
        {"question_id": "q1", "answer": "b", "feedback_shown": True},
    ]
    updated_mission = await update_mission_progress(user_id, 2, answers, mock_mission_repo)

    assert updated_mission is not None
    # The mission should now be marked as COMPLETED.
    assert updated_mission.status == MissionStatus.COMPLETE
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_update_mission_progress_all_answered_no_feedback(mock_mission_repo):
    user_id = "feedback_user"
    today = datetime.now(TARGET_TIMEZONE).date()
    questions = [Question(question_id=f"q{i}", question_text=f"Q{i}?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="c1", feedback_th="fb") for i in range(2)]
    mission_doc = DailyMissionDocument(user_id=user_id, date=today, questions=questions, status=MissionStatus.IN_PROGRESS)
    mock_mission_repo.find_mission.return_value = mission_doc

    # All questions answered, but one is missing feedback_shown = True
    answers = [
        {"question_id": "q0", "answer": "a", "feedback_shown": True},
        {"question_id": "q1", "answer": "b", "feedback_shown": False}, # Feedback not shown
    ]
    updated_mission = await update_mission_progress(user_id, 2, answers, mock_mission_repo)

    assert updated_mission is not None
    # Status should remain IN_PROGRESS because not all feedback has been viewed.
    assert updated_mission.status == MissionStatus.IN_PROGRESS
    mock_mission_repo.save_mission.assert_called_once()

@pytest.mark.asyncio
async def test_update_mission_progress_not_found(mock_mission_repo):
    mock_mission_repo.find_mission.return_value = None
    result = await update_mission_progress("ghost_user", 1, [], mock_mission_repo)
    assert result is None
    mock_mission_repo.save_mission.assert_not_called()

@pytest.mark.asyncio
async def test_archive_past_incomplete_missions(mock_mission_repo):
    mission1 = DailyMissionDocument(user_id="u1", date=date(2023,1,1), status=MissionStatus.IN_PROGRESS, questions=[])
    mission2 = DailyMissionDocument(user_id="u2", date=date(2023,1,2), status=MissionStatus.NOT_STARTED, questions=[])
    mock_mission_repo.get_missions_to_archive.return_value = [mission1, mission2]

    count = await archive_past_incomplete_missions(mock_mission_repo)
    
    assert count == 2
    assert mock_mission_repo.save_mission.call_count == 2
    # Verify that the status is updated to ARCHIVED
    first_call_args = mock_mission_repo.save_mission.call_args_list[0].args[0]
    assert first_call_args.status == MissionStatus.ARCHIVED 