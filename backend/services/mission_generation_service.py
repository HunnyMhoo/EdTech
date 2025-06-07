from datetime import datetime, timezone
from typing import Optional
import random
import asyncio

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question
from backend.repositories.question_repository import QuestionRepository
from backend.repositories.mission_repository import MissionRepository
from backend.services.utils import TARGET_TIMEZONE, get_current_time_in_target_timezone

# Custom Exceptions
class MissionGenerationError(Exception):
    """Base exception for mission generation issues."""
    pass

class NoQuestionsAvailableError(MissionGenerationError):
    """Raised when the question pool is empty or has insufficient questions."""
    pass

class MissionAlreadyExistsError(MissionGenerationError):
    """Raised when a mission for the user and current date already exists."""
    pass

async def generate_daily_mission(
    user_id: str,
    mission_repo: MissionRepository,
    question_repo: QuestionRepository,
    current_datetime_utc: Optional[datetime] = None
) -> DailyMissionDocument:
    """
    Generates and persists a new daily mission with 5 questions per user per day.
    Uses DailyMissionDocument and embeds full Question objects.
    """
    all_questions = await question_repo.get_all_questions()
    if not all_questions:
        raise NoQuestionsAvailableError("The question repository is empty. Cannot generate a mission.")

    if current_datetime_utc is None:
        current_datetime_utc = datetime.now(timezone.utc)

    mission_date = current_datetime_utc.astimezone(TARGET_TIMEZONE).date()

    if await mission_repo.find_mission(user_id, mission_date):
        raise MissionAlreadyExistsError(f"A mission for user '{user_id}' on {mission_date} already exists.")

    if len(all_questions) < 5:
        raise NoQuestionsAvailableError(f"Insufficient questions available ({len(all_questions)} found) to generate a mission of 5 questions.")

    question_ids = random.sample(list(all_questions.keys()), 5)
    
    mission_questions_tasks = [question_repo.get_question_by_id(qid) for qid in question_ids]
    mission_questions_results = await asyncio.gather(*mission_questions_tasks)

    mission_questions = [q for q in mission_questions_results if q is not None]
    
    if len(mission_questions) < 5:
        raise MissionGenerationError(f"Could not retrieve full question details for all selected IDs. Required 5, got {len(mission_questions)}.")

    new_mission = DailyMissionDocument(
        user_id=user_id,
        date=mission_date,
        questions=mission_questions,
        status=MissionStatus.NOT_STARTED,
        created_at=get_current_time_in_target_timezone(),
        updated_at=get_current_time_in_target_timezone()
    )

    await mission_repo.save_mission(new_mission)
    print(f"Successfully generated and saved new mission for user '{user_id}' for date {mission_date}.")
    return new_mission 