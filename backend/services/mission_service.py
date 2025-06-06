import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import asyncio

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question
from backend.repositories.question_repository import question_repository

# Define the target timezone: UTC+7
TARGET_TIMEZONE = timezone(timedelta(hours=7))

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
# In a real application, this would interact with MongoDB via a repository/ODM
# For this task, we'll use an in-memory list to simulate the database, storing DailyMissionDocument instances.
_mock_db_missions: List[DailyMissionDocument] = []

def get_question_details_by_id(question_id: str) -> Optional[Question]:
    """Retrieves a single question by its ID from the repository."""
    return question_repository.get_question_by_id(question_id)

def _find_mission_in_db(user_id: str, mission_date_target_tz: datetime) -> Optional[DailyMissionDocument]:
    """
    Simulates finding a mission in the database for a given user and date (comparing date parts in TARGET_TIMEZONE).
    """
    target_date_val = mission_date_target_tz.date()
    for mission_doc in _mock_db_missions:
        # Ensure stored 'date' is timezone-aware or consistently handled if it was stored as naive
        # Our DailyMissionDocument.date is datetime.date, so direct comparison is fine
        if mission_doc.user_id == user_id and mission_doc.date == target_date_val:
            return mission_doc
    return None

def _save_mission_to_db(mission_doc: DailyMissionDocument) -> DailyMissionDocument:
    """
    Simulates saving a mission to the database.
    If a mission with the same userId and date already exists, it updates it.
    Otherwise, it adds the new mission.
    """
    existing_mission_index = -1
    for i, m in enumerate(_mock_db_missions):
        if m.user_id == mission_doc.user_id and m.date == mission_doc.date:
            existing_mission_index = i
            break
    
    if existing_mission_index != -1:
        _mock_db_missions[existing_mission_index] = mission_doc
    else:
        _mock_db_missions.append(mission_doc)
    return mission_doc

async def _fetch_mission_from_db(user_id: str, target_date_utc0: datetime) -> Optional[DailyMissionDocument]:
    """
    Fetches a mission for a given user and date (represented as UTC midnight) from the mock DB.
    The date in the DB is effectively treated as representing the start of day in UTC+7.
    """
    target_date_in_target_tz = target_date_utc0.astimezone(TARGET_TIMEZONE)
    
    # print(f"DB Query (mock): Find mission for user_id={user_id} on date (TARGET_TIMEZONE)={target_date_in_target_tz.date()}")
    
    mission_doc = _find_mission_in_db(user_id=user_id, mission_date_target_tz=target_date_in_target_tz)
    
    return mission_doc

def get_utc7_today_date() -> datetime.date:
    """Calculates today's date in UTC+7."""
    return datetime.now(TARGET_TIMEZONE).date()

async def get_todays_mission_for_user(user_id: str) -> Optional[DailyMissionDocument]:
    """
    Retrieves today's (UTC+7) mission for a given user, including progress.
    """
    today_target_tz_date = get_utc7_today_date()
    
    # print(f"Service: Attempting to fetch mission for user {user_id} for date (UTC+7 today): {today_target_tz_date}")
    mission_doc = _find_mission_in_db(user_id, datetime.combine(today_target_tz_date, datetime.min.time(), tzinfo=TARGET_TIMEZONE))
            
    if not mission_doc:
        # print(f"Service: No mission found for user {user_id} for date {today_target_tz_date}. Attempting to generate one.")
        try:
            mission_doc = await generate_daily_mission(user_id)
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
    status: Optional[MissionStatus] = None
) -> Optional[DailyMissionDocument]:
    """
    Updates the progress of today's mission for a given user.
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await get_todays_mission_for_user(user_id)

    if not mission_doc:
        # Or raise an error: print(f"Service: No mission found to update progress for user {user_id} for date {today_target_tz_date}")
        return None

    mission_doc.current_question_index = current_question_index
    mission_doc.answers = answers
    if status:
        mission_doc.status = status
    mission_doc.updated_at = datetime.now(timezone.utc)

    _save_mission_to_db(mission_doc) # Save changes back to the mock DB
    # print(f"Service: Updated progress for user {user_id}. Index: {current_question_index}, Answers: {len(answers)}")
    return mission_doc

async def generate_daily_mission(user_id: str, current_datetime_utc: Optional[datetime] = None) -> DailyMissionDocument:
    """
    Generates and persists a new daily mission with 5 questions per user per day.
    Uses DailyMissionDocument and embeds full Question objects.
    """
    all_questions = question_repository.get_all_questions()
    if not all_questions:
        raise NoQuestionsAvailableError("The question repository is empty. Cannot generate a mission.")

    if current_datetime_utc is None:
        current_datetime_utc = datetime.now(timezone.utc)

    # We now check against the target timezone date.
    mission_date = current_datetime_utc.astimezone(TARGET_TIMEZONE).date()

    # Check if a mission for this user and date already exists
    if _find_mission_in_db(user_id, datetime.combine(mission_date, datetime.min.time(), tzinfo=TARGET_TIMEZONE)):
        raise MissionAlreadyExistsError(f"A mission for user '{user_id}' on {mission_date} already exists.")

    # Ensure we have enough questions to generate a mission
    if len(all_questions) < 5:
        raise NoQuestionsAvailableError(f"Insufficient questions available ({len(all_questions)} found) to generate a mission of 5 questions.")

    # Select 5 random question_ids
    question_ids = random.sample(list(all_questions.keys()), 5)
    
    # Fetch full question objects from the repository using the selected IDs
    mission_questions = [question_repository.get_question_by_id(qid) for qid in question_ids]
    # Filter out any potential None results if an ID somehow becomes invalid between sampling and fetching
    mission_questions = [q for q in mission_questions if q is not None]
    
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
    _save_mission_to_db(new_mission)
    print(f"Successfully generated and saved new mission for user '{user_id}' for date {mission_date}.")
    return new_mission

async def archive_past_incomplete_missions() -> int:
    """
    Archives missions from previous days (UTC+7) that are not yet complete or already archived.
    Returns the count of archived missions.
    """
    archived_count = 0
    today_utc7 = get_utc7_today_date()
    # print(f"Service: Running archive job for missions before date (UTC+7): {today_utc7}")

    missions_to_update: List[DailyMissionDocument] = []
    for mission_doc in _mock_db_missions:
        if mission_doc.date < today_utc7:
            if mission_doc.status not in [MissionStatus.COMPLETE, MissionStatus.ARCHIVED]:
                missions_to_update.append(mission_doc)
    
    for mission_doc in missions_to_update:
        mission_doc.status = MissionStatus.ARCHIVED
        mission_doc.updated_at = datetime.now(timezone.utc)
        _save_mission_to_db(mission_doc) # This will update the existing entry in _mock_db_missions
        archived_count += 1
        # print(f"Service: Archived mission for user {mission_doc.user_id} for date {mission_doc.date}")

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
    async def main():
        print("--- Running basic service tests ---")
        
        # Ensure the repository can load questions
        all_questions = question_repository.get_all_questions()
        if not all_questions:
            print("CRITICAL: Question repository failed to load any questions.")
            return
        print(f"Successfully loaded {len(all_questions)} questions from repository.")

        # Test mission generation
        test_user = "test_user_001"
        try:
            print(f"\nAttempting to generate a mission for {test_user}...")
            mission = await generate_daily_mission(test_user)
            print("Mission generated successfully.")
            
            # Test fetching the mission
            print(f"\nAttempting to fetch the mission for {test_user}...")
            fetched_mission = await get_todays_mission_for_user(test_user)
            assert fetched_mission is not None
            assert fetched_mission.user_id == test_user
            print("Mission fetched successfully.")

            # Test that generating again fails
            print(f"\nAttempting to generate mission again (should fail)...")
            try:
                await generate_daily_mission(test_user)
            except MissionAlreadyExistsError:
                print("Correctly caught MissionAlreadyExistsError.")

        except Exception as e:
            print(f"An unexpected error occurred during testing: {e}")

        print("\n--- Basic service tests finished ---")

    asyncio.run(main()) 