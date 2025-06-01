import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question # Added Question import

# Define the target timezone: UTC+7
TARGET_TIMEZONE = timezone(timedelta(hours=7))

# Define a base path for data files, assuming this script is in backend/services/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QUESTIONS_FILE_PATH = DATA_DIR / "gat_questions.csv"

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

# --- Global Question Cache ---
_ALL_QUESTIONS: Dict[str, Question] = {}

def _load_questions_from_csv(file_path: Path) -> Dict[str, Question]:
    """
    Loads all question details from a CSV file into a dictionary.
    Assumes CSV has headers: question_id, question_text, skill_area, difficulty_level.
    """
    questions: Dict[str, Question] = {}
    if not file_path.exists():
        raise FileNotFoundError(f"Question file not found: {file_path}")
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('question_id') and row.get('question_text'): # Basic validation
                    try:
                        question = Question(
                            question_id=row['question_id'],
                            question_text=row['question_text'],
                            skill_area=row.get('skill_area', 'N/A'),
                            difficulty_level=int(row.get('difficulty_level', 0))
                        )
                        questions[question.question_id] = question
                    except ValueError as ve:
                        print(f"Warning: Skipping row due to data conversion error: {row} - {ve}")
                    except Exception as e_row: # Catch other Pydantic validation or unexpected errors per row
                        print(f"Warning: Skipping row due to error: {row} - {e_row}")
    except Exception as e:
        # Log this error appropriately
        raise MissionGenerationError(f"Critical error reading or parsing question file {file_path}: {e}") from e
    
    if not questions:
        # This is a critical situation if the file exists but no questions could be loaded.
        raise NoQuestionsAvailableError(f"No valid questions could be loaded from {file_path}.")
        
    return questions

def _initialize_question_cache():
    """Initializes the global question cache if it's empty."""
    global _ALL_QUESTIONS
    if not _ALL_QUESTIONS:
        try:
            _ALL_QUESTIONS = _load_questions_from_csv(QUESTIONS_FILE_PATH)
            if _ALL_QUESTIONS:
                print(f"Successfully loaded {len(_ALL_QUESTIONS)} questions into cache.")
            else:
                # This case should ideally be caught by _load_questions_from_csv raising an error
                print(f"Warning: Question cache initialized but is empty after loading from {QUESTIONS_FILE_PATH}.")
        except Exception as e:
            # Log this critical error. The application might not function correctly without questions.
            print(f"CRITICAL: Failed to initialize question cache: {e}")
            # Depending on application requirements, you might re-raise or handle this to prevent startup.
            # For now, we'll let it proceed, but services relying on questions will fail.
            _ALL_QUESTIONS = {} # Ensure it's an empty dict if loading fails

# Initialize cache when module is loaded.
_initialize_question_cache()

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
    if not _ALL_QUESTIONS: # Check if cache is populated
        # Attempt to re-initialize if it's empty; might indicate a startup loading issue
        print("Warning: Question cache was empty during mission generation. Attempting to re-initialize.")
        _initialize_question_cache()
        if not _ALL_QUESTIONS:
            raise NoQuestionsAvailableError(
                "Question cache is empty and could not be initialized. Cannot generate mission."
            )

    if current_datetime_utc:
        now_utc = current_datetime_utc.replace(tzinfo=timezone.utc)
    else:
        now_utc = datetime.now(timezone.utc)

    now_target_tz = now_utc.astimezone(TARGET_TIMEZONE)
    today_target_tz_date = now_target_tz.date()

    existing_mission = _find_mission_in_db(user_id, now_target_tz)
    if existing_mission:
        raise MissionAlreadyExistsError(
            f"Mission for user {user_id} on {today_target_tz_date} already exists."
        )

    # Use the pre-loaded questions from the cache
    all_question_ids = list(_ALL_QUESTIONS.keys())

    if not all_question_ids or len(all_question_ids) < 5:
        raise NoQuestionsAvailableError(
            "Not enough questions available in the pool to generate a mission."
        )

    selected_question_ids = random.sample(all_question_ids, 5)
    selected_questions: List[Question] = [_ALL_QUESTIONS[qid] for qid in selected_question_ids if qid in _ALL_QUESTIONS]

    if len(selected_questions) < 5:
        # This should ideally not happen if random.sample worked correctly and _ALL_QUESTIONS is consistent
        raise MissionGenerationError(
            f"Could not retrieve full question details for all selected IDs. Expected 5, got {len(selected_questions)}."
        )
    
    # Timestamps should be timezone-aware UTC
    utc_now = datetime.now(timezone.utc)

    new_mission_doc = DailyMissionDocument(
        user_id=user_id,
        date=today_target_tz_date,
        questions=selected_questions, # Embed full question objects
        status=MissionStatus.NOT_STARTED,
        created_at=utc_now,
        updated_at=utc_now
    )

    saved_mission = _save_mission_to_db(new_mission_doc)
    # print(f"Service: Generated and saved new mission for user {user_id} for date {today_target_tz_date}")
    return saved_mission

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
    # Example Usage & Manual Verification Simulation
    
    # Ensure the cache is loaded for testing (it should be by module import, but good for clarity)
    if not _ALL_QUESTIONS:
        print("Main: Question cache empty, attempting to load for test...")
        _initialize_question_cache() # Should load questions

    if not _ALL_QUESTIONS:
        print("Main: CRITICAL - Failed to load questions for the test script. Exiting.")
        exit()
        
    print(f"Available questions in cache: {len(_ALL_QUESTIONS)}")

    test_user_id = "test_user_main_001"
    print(f"--- Attempting to generate mission for user: {test_user_id} ---")
    try:
        mission = asyncio.run(generate_daily_mission(test_user_id))
        print("Mission generated successfully:")
        print(mission.model_dump_json(indent=2))
    except MissionGenerationError as e:
        print(f"Error generating mission: {e}")

    print(f"\n--- Attempting to generate mission again for user: {test_user_id} (should fail) ---")
    try:
        mission = asyncio.run(generate_daily_mission(test_user_id))
        print("Mission generated successfully (this should not happen):")
        print(mission.model_dump_json(indent=2))
    except MissionAlreadyExistsError as e:
        print(f"Correctly caught error for existing mission: {e}")
    except MissionGenerationError as e:
        print(f"Error generating mission: {e}")

    # Simulate time passing to the next day for UTC+7
    # Current UTC time is X. If X is 18:00 UTC, it's 01:00 UTC+7 (next day).
    # If X is 16:00 UTC, it's 23:00 UTC+7 (same day).
    # We need to advance time enough so that `now_utc.astimezone(TARGET_TIMEZONE).date()` is different.
    # Let's use a fixed past time for the first mission to make it testable.
    
    _mock_db_missions = [] # Clear DB for next test
    fixed_time_yesterday_utc = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc) # 17:00 UTC+7 on Jan 1st
    
    print(f"\n--- Generating mission for {test_user_id} at a fixed past time: {fixed_time_yesterday_utc.isoformat()} ---")
    try:
        mission_past = asyncio.run(generate_daily_mission(test_user_id, current_datetime_utc=fixed_time_yesterday_utc))
        print("Past mission generated successfully:")
        print(mission_past.model_dump_json(indent=2))
    except MissionGenerationError as e:
        print(f"Error generating past mission: {e}")

    # Now try to generate for "today" relative to current execution, which should be different from Jan 1st, 2023
    print(f"\n--- Generating mission for {test_user_id} for current time (should be a new day) ---")
    try:
        mission_today = asyncio.run(generate_daily_mission(test_user_id)) # Uses current time
        print("Mission for current day generated successfully:")
        print(mission_today.model_dump_json(indent=2))
        assert mission_today.date != mission_past.date
    except MissionGenerationError as e:
        print(f"Error generating mission for current day: {e}")

    print(f"\n--- Verifying mock DB content ---")
    for m in _mock_db_missions:
        print(f" - User: {m.user_id}, Date: {m.date.isoformat()}, Questions: {len(m.questions)}, Status: {m.status.value}")

    # Test with insufficient questions
    _mock_db_missions.clear() # Clear DB
    temp_questions_file = DATA_DIR / "temp_few_questions.csv"
    with open(temp_questions_file, mode='w', encoding='utf-8') as f:
        f.write("question_id\nQ1\nQ2\nQ3") # Only 3 questions
    
    print(f"\n--- Attempting to generate mission with insufficient questions ({temp_questions_file.name}) ---")
    original_questions_file_path = QUESTIONS_FILE_PATH
    try:
        QUESTIONS_FILE_PATH = temp_questions_file # Temporarily override
        generate_daily_mission("student_few_q")
    except NoQuestionsAvailableError as e:
        print(f"Correctly caught error for insufficient questions: {e}")
    finally:
        QUESTIONS_FILE_PATH = original_questions_file_path # Restore
        if temp_questions_file.exists():
            temp_questions_file.unlink()

    print("\nDemo finished.")
    asyncio.run(main_test_logic()) 