import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

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

def _load_question_ids_from_csv(file_path: Path) -> List[str]:
    """
    Loads question IDs from a CSV file.
    Assumes the CSV has a header and the first column is 'question_id'.
    """
    question_ids: List[str] = []
    if not file_path.exists():
        # In a real scenario, might want to log this or handle more gracefully
        raise FileNotFoundError(f"Question file not found: {file_path}")
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'question_id' in row and row['question_id']:
                    question_ids.append(row['question_id'])
    except Exception as e:
        # Log error, e.g., logging.error(f"Could not read questions CSV: {e}")
        raise MissionGenerationError(f"Error reading question file: {e}") from e
    return question_ids

# --- Mock Database Interaction ---
# In a real application, this would interact with MongoDB via a repository/ODM
# For this task, we'll use an in-memory dictionary to simulate the database.
_mock_db: Dict[str, List[Dict[str, Any]]] = {
    "daily_missions": []
}

def _find_mission_in_db(user_id: str, mission_date: datetime) -> Optional[Dict[str, Any]]:
    """
    Simulates finding a mission in the database for a given user and date (ignoring time part).
    """
    for mission in _mock_db["daily_missions"]:
        if mission["userId"] == user_id and mission["date"].date() == mission_date.date():
            return mission
    return None

def _save_mission_to_db(mission_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates saving a mission to the database.
    """
    _mock_db["daily_missions"].append(mission_data)
    return mission_data
# --- End Mock Database Interaction ---


def generate_daily_mission(user_id: str, current_datetime_utc: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Generates and persists a new daily mission with 5 questions per user per day.

    Args:
        user_id: The ID of the user for whom to generate the mission.
        current_datetime_utc: Optional current UTC datetime, for testing.
                               If None, datetime.utcnow() is used.

    Returns:
        A dictionary representing the newly created (or existing if not overwriting) daily mission.

    Raises:
        MissionAlreadyExistsError: If a mission for today already exists for the user.
        NoQuestionsAvailableError: If not enough questions are available in the GAT pool.
        FileNotFoundError: If the questions CSV file is not found.
        MissionGenerationError: For other errors during generation.
    """
    if current_datetime_utc:
        now_utc = current_datetime_utc.replace(tzinfo=timezone.utc)
    else:
        now_utc = datetime.now(timezone.utc)

    # Convert to target timezone (UTC+7) to determine the "current day"
    now_target_tz = now_utc.astimezone(TARGET_TIMEZONE)
    today_target_tz_date = now_target_tz.date()

    # Simulate checking the database
    # In a real app, this would be:
    # mission_date_for_query = datetime(today_target_tz_date.year, today_target_tz_date.month, today_target_tz_date.day, tzinfo=TARGET_TIMEZONE)
    # existing_mission = mission_repository.find_by_userid_and_date(user_id, mission_date_for_query)
    existing_mission = _find_mission_in_db(user_id, now_target_tz)

    if existing_mission:
        # As per discussion, fail if mission exists.
        # Alternatively, could return the existing mission: return existing_mission
        raise MissionAlreadyExistsError(
            f"Daily mission for user {user_id} on {today_target_tz_date.isoformat()} already exists."
        )

    # Load question IDs from the GAT pool (CSV file)
    all_question_ids = _load_question_ids_from_csv(QUESTIONS_FILE_PATH)

    if not all_question_ids or len(all_question_ids) < 5:
        raise NoQuestionsAvailableError(
            f"Not enough questions available in the GAT pool. Found {len(all_question_ids)}, need 5."
        )

    # Select 5 random, unique question IDs
    try:
        selected_question_ids = random.sample(all_question_ids, 5)
    except ValueError as e:
        # This can happen if len(all_question_ids) < 5, though checked above, good to be defensive.
        raise NoQuestionsAvailableError(
            f"Could not select 5 unique questions. Pool size: {len(all_question_ids)}. Error: {e}"
        ) from e

    # Create the new daily mission object
    # The 'date' field should store the date in UTC for consistency in the DB,
    # or as a date object if the DB supports it well for timezone-naive date queries.
    # For this example, storing the target timezone's date object.
    # When querying, ensure to use the same timezone logic.
    new_mission_data = {
        "userId": user_id,
        "date": now_target_tz, # Storing with timezone info, or just now_target_tz.date()
        "questionIds": selected_question_ids,
        "status": "not_started",  # As per Task 1 schema
        "createdAt": now_utc      # Timestamp of creation in UTC
    }

    # Persist to database (simulated)
    created_mission = _save_mission_to_db(new_mission_data)

    return created_mission

if __name__ == '__main__':
    # Example Usage & Manual Verification Simulation
    print(f"Loading questions from: {QUESTIONS_FILE_PATH}")
    
    # Ensure data directory and file exist for this example to run from anywhere
    if not QUESTIONS_FILE_PATH.parent.exists():
        QUESTIONS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not QUESTIONS_FILE_PATH.exists():
        print(f"Mock questions file {QUESTIONS_FILE_PATH} not found. Creating a dummy one for the example.")
        with open(QUESTIONS_FILE_PATH, mode='w', encoding='utf-8') as f:
            f.write("question_id,question_text,skill_area,difficulty_level\n")
            for i in range(1, 11):
                f.write("TESTQ{:03d},\"Test question {}\TestSkill,{}\n".format(i, i, i%3+1))

    test_user_id = "student123"
    print(f"--- Attempting to generate mission for user: {test_user_id} ---")
    try:
        mission = generate_daily_mission(test_user_id)
        print("Mission generated successfully:")
        print(mission)
    except MissionGenerationError as e:
        print(f"Error generating mission: {e}")

    print(f"\n--- Attempting to generate mission again for user: {test_user_id} (should fail) ---")
    try:
        mission = generate_daily_mission(test_user_id)
        print("Mission generated successfully (this should not happen):")
        print(mission)
    except MissionAlreadyExistsError as e:
        print(f"Correctly caught error for existing mission: {e}")
    except MissionGenerationError as e:
        print(f"Error generating mission: {e}")

    # Simulate time passing to the next day for UTC+7
    # Current UTC time is X. If X is 18:00 UTC, it's 01:00 UTC+7 (next day).
    # If X is 16:00 UTC, it's 23:00 UTC+7 (same day).
    # We need to advance time enough so that `now_utc.astimezone(TARGET_TIMEZONE).date()` is different.
    # Let's use a fixed past time for the first mission to make it testable.
    
    _mock_db["daily_missions"] = [] # Clear DB for next test
    fixed_time_yesterday_utc = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc) # 17:00 UTC+7 on Jan 1st
    
    print(f"\n--- Generating mission for {test_user_id} at a fixed past time: {fixed_time_yesterday_utc.isoformat()} ---")
    try:
        mission_past = generate_daily_mission(test_user_id, current_datetime_utc=fixed_time_yesterday_utc)
        print("Past mission generated successfully:")
        print(mission_past)
    except MissionGenerationError as e:
        print(f"Error generating past mission: {e}")

    # Now try to generate for "today" relative to current execution, which should be different from Jan 1st, 2023
    print(f"\n--- Generating mission for {test_user_id} for current time (should be a new day) ---")
    try:
        mission_today = generate_daily_mission(test_user_id) # Uses current time
        print("Mission for current day generated successfully:")
        print(mission_today)
        assert mission_today["date"].date() != mission_past["date"].date()
    except MissionGenerationError as e:
        print(f"Error generating mission for current day: {e}")

    print(f"\n--- Verifying mock DB content ---")
    for m in _mock_db["daily_missions"]:
        print(f" - User: {m['userId']}, Date: {m['date'].isoformat()}, Questions: {len(m['questionIds'])}")

    # Test with insufficient questions
    _mock_db["daily_missions"] = [] # Clear DB
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