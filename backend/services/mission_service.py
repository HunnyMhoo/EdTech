import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import asyncio
from fastapi import Depends

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question
from backend.repositories.question_repository import QuestionRepository
from backend.repositories.mission_repository import MissionRepository

# Define the target timezone: UTC+7
TARGET_TIMEZONE = timezone(timedelta(hours=7))

# Instantiate repositories. In the next phase, this will be handled by Dependency Injection.
# mission_repo = MissionRepository() # This will be removed and injected.

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

# --- Mock Database Interaction -- -
# This section has been replaced by the MissionRepository.
# The in-memory list `_mock_db_missions` and functions `_find_mission_in_db`,
# `_save_mission_to_db`, and `_fetch_mission_from_db` have been removed.

async def get_question_details_by_id(
    question_id: str,
    question_repo: QuestionRepository
) -> Optional[Question]:
    """Retrieves a single question by its ID from the repository."""
    return await question_repo.get_question_by_id(question_id)

def get_utc7_today_date() -> datetime.date:
    """Calculates today's date in UTC+7."""
    return datetime.now(TARGET_TIMEZONE).date()

async def get_todays_mission_for_user(
    user_id: str,
    mission_repo: MissionRepository,
    question_repo: QuestionRepository
) -> Optional[DailyMissionDocument]:
    """
    Retrieves today's (UTC+7) mission for a given user, including progress.
    If no mission exists, it attempts to generate one.
    """
    today_target_tz_date = get_utc7_today_date()
    
    # print(f"Service: Attempting to fetch mission for user {user_id} for date (UTC+7 today): {today_target_tz_date}")
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)
            
    if not mission_doc:
        # print(f"Service: No mission found for user {user_id} for date {today_target_tz_date}. Attempting to generate one.")
        try:
            mission_doc = await generate_daily_mission(
                user_id=user_id,
                mission_repo=mission_repo,
                question_repo=question_repo
            )
            # print(f"Service: Successfully generated mission for user {user_id} on demand.")
        except MissionGenerationError as e:
            # print(f"Service: Error generating mission on demand for user {user_id}: {e}")
            # If generation fails (e.g., no questions), we still return None, 
            # and the route will raise a 404 with a specific message from the exception if possible,
            # or the generic "No mission found" if generate_daily_mission doesn't raise an HTTP-friendly error.
            # For now, the route will handle the 404 if mission_doc remains None.
            pass # Let it return None, route will handle 404
        
    return mission_doc

async def update_mission_progress(
    user_id: str,
    current_question_index: int,
    answers: List[Dict[str, Any]],
    mission_repo: MissionRepository,
    status: Optional[MissionStatus] = None
) -> Optional[DailyMissionDocument]:
    """
    Updates the progress of today's mission for a given user.
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)

    if not mission_doc:
        # Or raise an error: print(f"Service: No mission found to update progress for user {user_id} for date {today_target_tz_date}")
        return None

    mission_doc.current_question_index = current_question_index
    mission_doc.answers = answers
    if status:
        mission_doc.status = status
    mission_doc.updated_at = datetime.now(timezone.utc)

    await mission_repo.save_mission(mission_doc)
    # print(f"Service: Updated progress for user {user_id}. Index: {current_question_index}, Answers: {len(answers)}")
    return mission_doc

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

    # We now check against the target timezone date.
    mission_date = current_datetime_utc.astimezone(TARGET_TIMEZONE).date()

    # Check if a mission for this user and date already exists
    if await mission_repo.find_mission(user_id, mission_date):
        raise MissionAlreadyExistsError(f"A mission for user '{user_id}' on {mission_date} already exists.")

    # Ensure we have enough questions to generate a mission
    if len(all_questions) < 5:
        raise NoQuestionsAvailableError(f"Insufficient questions available ({len(all_questions)} found) to generate a mission of 5 questions.")

    # Select 5 random question_ids
    question_ids = random.sample(list(all_questions.keys()), 5)
    
    # Fetch full question objects from the repository using the selected IDs
    mission_questions_tasks = [question_repo.get_question_by_id(qid) for qid in question_ids]
    mission_questions_results = await asyncio.gather(*mission_questions_tasks)

    # Filter out any potential None results if an ID somehow becomes invalid between sampling and fetching
    mission_questions = [q for q in mission_questions_results if q is not None]
    
    if len(mission_questions) < 5:
        # This is an edge case that should rarely happen if the repository is consistent
        raise MissionGenerationError(f"Could not retrieve full question details for all selected IDs. Required 5, got {len(mission_questions)}.")

    # Create the mission document
    new_mission = DailyMissionDocument(
        user_id=user_id,
        date=mission_date,
        questions=mission_questions,
        status=MissionStatus.NOT_STARTED,
        created_at=current_datetime_utc.astimezone(TARGET_TIMEZONE),
        updated_at=current_datetime_utc.astimezone(TARGET_TIMEZONE)
    )

    # Persist the new mission
    await mission_repo.save_mission(new_mission)
    print(f"Successfully generated and saved new mission for user '{user_id}' for date {mission_date}.")
    return new_mission

async def archive_past_incomplete_missions(mission_repo: MissionRepository) -> int:
    """
    Archives missions from previous days (UTC+7) that are not yet complete or already archived.
    Returns the count of archived missions.
    """
    archived_count = 0
    today_utc7 = get_utc7_today_date()
    # print(f"Service: Running archive job for missions before date (UTC+7): {today_utc7}")

    missions_to_update = await mission_repo.get_missions_to_archive(today_utc7)
    
    if not missions_to_update:
        return 0

    # In a real DB, this could be a single bulk update operation.
    # Here, we save one by one.
    update_tasks = []
    for mission_doc in missions_to_update:
        mission_doc.status = MissionStatus.ARCHIVED
        mission_doc.updated_at = datetime.now(timezone.utc)
        update_tasks.append(mission_repo.save_mission(mission_doc))
    
    await asyncio.gather(*update_tasks)
    
    archived_count = len(missions_to_update)

    # print(f"Service: Archived {archived_count} missions.")
    return archived_count

# --- Placeholder for other functions if they were present and needed changes ---
# For example, the original file had placeholders or other utility functions.
# We'll keep the structure, but the primary focus was on the core mission logic.

# (The old generate_daily_mission_for_user and related get_utc7_today_midnight_utc0 
# seem to be replaced by or integrated into the updated generate_daily_mission 
# and get_todays_mission_for_user that use DailyMissionDocument.
# The old _fetch_mission_from_db that returned the local DailyMission is also replaced.)

# Keep the main logic from original generate_daily_mission, but adapt it
# to use the new Pydantic model and mock DB functions.
# The function previously named generate_daily_mission has been updated above.

# Ensure all functions that interact with missions now use DailyMissionDocument
# and the new mock DB structure.
# Example: A function to get all missions for a user (if it existed) would also need updating.
# For now, the provided functions (get_todays_mission_for_user, update_mission_progress, generate_daily_mission)
# are the main ones interacting with the mission data.

if __name__ == '__main__':
    # This is a basic test runner for the service.
    # In a real application, you would have a more robust test suite.
    # This section needs to be updated to work with the new DI-based functions.
    # It is left here conceptually but will not run without providing repository instances.
    async def main():
        print("--- Running basic service tests ---")
        
        # This test runner is now broken because it cannot provide the repository dependencies.
        # It should be replaced with proper tests in the test suite.
        print("!!! This manual test runner is deprecated and will not work correctly without refactoring. !!!")
        print("!!! Please rely on the pytest suite for testing. !!!")

    asyncio.run(main()) 