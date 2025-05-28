import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os
import csv
import pytest
import asyncio

# Adjust the Python path to import from backend.services
import sys
# Assuming tests are in backend/tests/unit/ and services in backend/services/
SERVICE_PATH = Path(__file__).resolve().parent.parent.parent / "services"
sys.path.insert(0, str(SERVICE_PATH))

# Now import from mission_service
from mission_service import (
    generate_daily_mission,
    _load_question_ids_from_csv,
    MissionAlreadyExistsError,
    NoQuestionsAvailableError,
    MissionGenerationError,
    TARGET_TIMEZONE,
    _mock_db, # For clearing between tests
    archive_past_incomplete_missions,
    _mock_db_missions, # For test setup and verification
    get_utc7_today_date,
    _save_mission_to_db # To help in direct manipulation for tests
)

from backend.models.daily_mission import DailyMissionDocument, MissionStatus

# Test data
MOCK_GAT_QUESTIONS_CSV_CONTENT_VALID = (
    "question_id,question_text,skill_area,difficulty_level\n"
    "GATQ001,Text1,Skill1,1\n"
    "GATQ002,Text2,Skill1,2\n"
    "GATQ003,Text3,Skill2,1\n"
    "GATQ004,Text4,Skill2,2\n"
    "GATQ005,Text5,Skill3,3\n"
    "GATQ006,Text6,Skill1,1\n"
    "GATQ007,Text7,Skill2,2\n"
    "GATQ008,Text8,Skill3,3\n"
    "GATQ009,Text9,Skill1,1\n"
    "GATQ010,Text10,Skill2,2\n"
)

MOCK_GAT_QUESTIONS_CSV_CONTENT_INSUFFICIENT = (
    "question_id,question_text,skill_area,difficulty_level\n"
    "GATQ001,Text1,Skill1,1\n"
    "GATQ002,Text2,Skill1,2\n"
    "GATQ003,Text3,Skill2,1\n"
)
MOCK_GAT_QUESTIONS_CSV_CONTENT_MALFORMED = (
    "id,text,skill\n"
    "GATQ001,Text1,Skill1\n"
)

class TestMissionService(unittest.TestCase):

    def setUp(self):
        # Reset the mock database before each test
        _mock_db["daily_missions"] = []
        # Ensure a clean slate for where the QUESTIONS_FILE_PATH might point
        self.test_data_dir = Path(__file__).resolve().parent / "test_data_temp"
        self.test_data_dir.mkdir(exist_ok=True)
        self.mock_questions_file_path = self.test_data_dir / "mock_gat_questions.csv"

    def tearDown(self):
        # Clean up created mock files and directory
        if self.mock_questions_file_path.exists():
            self.mock_questions_file_path.unlink()
        # Cleanup other files if any created directly in test_data_dir
        for item in self.test_data_dir.iterdir():
            item.unlink()
        self.test_data_dir.rmdir()

    def _create_mock_csv(self, content):
        with open(self.mock_questions_file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(content)
        return self.mock_questions_file_path

    # --- Tests for _load_question_ids_from_csv --- 
    def test_load_question_ids_from_csv_success(self):
        path = self._create_mock_csv(MOCK_GAT_QUESTIONS_CSV_CONTENT_VALID)
        question_ids = _load_question_ids_from_csv(path)
        self.assertEqual(len(question_ids), 10)
        self.assertIn("GATQ001", question_ids)
        self.assertIn("GATQ010", question_ids)

    def test_load_question_ids_from_csv_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            _load_question_ids_from_csv(Path("non_existent_file.csv"))

    def test_load_question_ids_from_csv_malformed_missing_column(self):
        path = self._create_mock_csv(MOCK_GAT_QUESTIONS_CSV_CONTENT_MALFORMED)
        # This should still parse but yield no question_ids if 'question_id' column is strictly checked
        # The current implementation of _load_question_ids_from_csv checks `if 'question_id' in row`
        # so it will simply return an empty list if the column name is different.
        # If strict validation is needed (e.g., must have 'question_id'), the function should raise an error.
        # For now, testing current behavior:
        ids = _load_question_ids_from_csv(path)
        self.assertEqual(len(ids), 0) 
        # If we wanted it to fail, we might do:
        # with self.assertRaisesRegex(MissionGenerationError, "Error reading question file"):
        #    _load_question_ids_from_csv(path)

    def test_load_question_ids_from_csv_empty_file(self):
        path = self._create_mock_csv("question_id\n") # Header only
        question_ids = _load_question_ids_from_csv(path)
        self.assertEqual(len(question_ids), 0)

    # --- Tests for generate_daily_mission --- 
    @patch('mission_service._load_question_ids_from_csv')
    @patch('mission_service._save_mission_to_db', side_effect=lambda x: x) # Mock save
    @patch('mission_service._find_mission_in_db', return_value=None) # Mock find
    def test_generate_daily_mission_success(self, mock_find, mock_save, mock_load_csv):
        mock_load_csv.return_value = [f"QID{i:03}" for i in range(10)]
        user_id = "user1"
        now_utc = datetime(2023, 10, 26, 10, 0, 0, tzinfo=timezone.utc) # 17:00 UTC+7

        mission = generate_daily_mission(user_id, current_datetime_utc=now_utc)

        self.assertEqual(mission["userId"], user_id)
        self.assertEqual(len(mission["questionIds"]), 5)
        self.assertTrue(all(qid.startswith("QID") for qid in mission["questionIds"]))
        self.assertEqual(mission["status"], "not_started")
        self.assertEqual(mission["createdAt"], now_utc)
        
        # Check date is correct for UTC+7
        expected_date_target_tz = now_utc.astimezone(TARGET_TIMEZONE)
        self.assertEqual(mission["date"].date(), expected_date_target_tz.date())
        self.assertEqual(mission["date"].tzinfo, TARGET_TIMEZONE)
        
        mock_load_csv.assert_called_once()
        mock_find.assert_called_once_with(user_id, now_utc.astimezone(TARGET_TIMEZONE))
        mock_save.assert_called_once()

    @patch('mission_service._find_mission_in_db')
    def test_generate_mission_already_exists(self, mock_find):
        user_id = "user_exists"
        now_utc = datetime(2023, 10, 26, 10, 0, 0, tzinfo=timezone.utc)
        existing_mission_date = now_utc.astimezone(TARGET_TIMEZONE)
        mock_find.return_value = {
            "userId": user_id, 
            "date": existing_mission_date, 
            "questionIds": ["Q1", "Q2", "Q3", "Q4", "Q5"]
        }

        with self.assertRaises(MissionAlreadyExistsError):
            generate_daily_mission(user_id, current_datetime_utc=now_utc)
        mock_find.assert_called_once_with(user_id, existing_mission_date)

    @patch('mission_service._load_question_ids_from_csv', return_value=[])
    @patch('mission_service._find_mission_in_db', return_value=None)
    def test_generate_mission_no_questions_available_empty_pool(self, mock_find, mock_load_csv):
        with self.assertRaises(NoQuestionsAvailableError):
            generate_daily_mission("user_empty_pool")

    @patch('mission_service._load_question_ids_from_csv', return_value=["Q1", "Q2", "Q3"]) # Only 3 questions
    @patch('mission_service._find_mission_in_db', return_value=None)
    def test_generate_mission_no_questions_available_insufficient_pool(self, mock_find, mock_load_csv):
        with self.assertRaises(NoQuestionsAvailableError):
            generate_daily_mission("user_insufficient_pool")

    @patch('mission_service.QUESTIONS_FILE_PATH', Path("non_existent_file.csv"))
    @patch('mission_service._find_mission_in_db', return_value=None)
    def test_generate_mission_questions_file_not_found(self, mock_find):
        # This tests if _load_question_ids_from_csv (when not mocked) raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            generate_daily_mission("user_file_not_found")

    @patch('mission_service._load_question_ids_from_csv')
    @patch('mission_service._save_mission_to_db', side_effect=lambda x: x)
    @patch('mission_service._find_mission_in_db', return_value=None)
    def test_mission_date_uses_target_timezone(self, mock_find, mock_save, mock_load_csv):
        mock_load_csv.return_value = [f"QID{i}" for i in range(10)]
        user_id = "user_tz_test"
        
        # 20:00 UTC on Oct 26 is 03:00 UTC+7 on Oct 27
        time_utc = datetime(2023, 10, 26, 20, 0, 0, tzinfo=timezone.utc)
        mission = generate_daily_mission(user_id, current_datetime_utc=time_utc)
        self.assertEqual(mission["date"].date(), datetime(2023, 10, 27).date())
        self.assertEqual(mission["date"].tzinfo, TARGET_TIMEZONE)

        # 15:00 UTC on Oct 26 is 22:00 UTC+7 on Oct 26
        time_utc_same_day = datetime(2023, 10, 26, 15, 0, 0, tzinfo=timezone.utc)
        _mock_db["daily_missions"] = [] # Reset for this sub-test
        mock_find.reset_mock() # Reset call count for find for this specific call
        mock_find.return_value = None # Ensure it doesn't think mission exists
        mission_same_day = generate_daily_mission(user_id, current_datetime_utc=time_utc_same_day)
        self.assertEqual(mission_same_day["date"].date(), datetime(2023, 10, 26).date())
        self.assertEqual(mission_same_day["date"].tzinfo, TARGET_TIMEZONE)

    @patch('mission_service._load_question_ids_from_csv')
    @patch('mission_service._save_mission_to_db', side_effect=lambda x: x)
    @patch('mission_service._find_mission_in_db') # side_effect to control returns
    def test_new_day_new_mission(self, mock_find, mock_save, mock_load_csv):
        mock_load_csv.return_value = [f"QID{i}" for i in range(10)]
        user_id = "user_new_day"

        # Day 1: Oct 26th, 22:00 UTC+7 (15:00 UTC)
        time_day1_utc = datetime(2023, 10, 26, 15, 0, 0, tzinfo=timezone.utc)
        # On first call, no mission exists
        mock_find.return_value = None 
        mission1 = generate_daily_mission(user_id, current_datetime_utc=time_day1_utc)
        self.assertEqual(mission1["date"].astimezone(TARGET_TIMEZONE).date(), datetime(2023, 10, 26).date())

        # Prepare mock_find for the second call: mission1 now exists for its date
        # The _find_mission_in_db in service uses .date() comparison with the mission_date (which is tz-aware)
        # So, for the next day, it should not find mission1.
        def find_side_effect(uid, mdate):
            if uid == user_id and mdate.date() == mission1["date"].date():
                return mission1 # Found if querying for the same date
            return None # Not found if querying for a different date
        mock_find.side_effect = find_side_effect

        # Day 2: Oct 27th, 03:00 UTC+7 (Oct 26th, 20:00 UTC)
        time_day2_utc = datetime(2023, 10, 26, 20, 0, 0, tzinfo=timezone.utc)
        mission2 = generate_daily_mission(user_id, current_datetime_utc=time_day2_utc)
        self.assertEqual(mission2["date"].astimezone(TARGET_TIMEZONE).date(), datetime(2023, 10, 27).date())
        
        self.assertNotEqual(mission1["date"].date(), mission2["date"].date())
        self.assertNotEqual(mission1["questionIds"], mission2["questionIds"])
        self.assertEqual(mock_save.call_count, 2) # Saved twice

# Helper to create mission documents for testing
def _create_mission_doc(
    user_id: str, 
    mission_date: date, 
    status: MissionStatus,
    q_ids: list = ["q1", "q2", "q3", "q4", "q5"]
) -> DailyMissionDocument:
    return DailyMissionDocument(
        user_id=user_id,
        date=mission_date,
        question_ids=q_ids,
        status=status,
        created_at=datetime.now(timezone.utc) - timedelta(days=10), # ensure created_at is in past
        updated_at=datetime.now(timezone.utc) - timedelta(days=10)  # ensure updated_at is in past
    )

@pytest.fixture(autouse=True)
def clear_mock_db_before_each_test():
    """Ensures the mock DB is empty before each test run."""
    _mock_db_missions.clear()
    yield
    _mock_db_missions.clear()

@pytest.mark.asyncio
async def test_archive_no_missions():
    """Test archiving when there are no missions in the DB."""
    archived_count = await archive_past_incomplete_missions()
    assert archived_count == 0
    assert len(_mock_db_missions) == 0

@pytest.mark.asyncio
async def test_archive_only_current_day_missions():
    """Test that missions from today (UTC+7) are not archived."""
    today_utc7 = get_utc7_today_date()
    _mock_db_missions.append(_create_mission_doc("user1", today_utc7, MissionStatus.NOT_STARTED))
    _mock_db_missions.append(_create_mission_doc("user2", today_utc7, MissionStatus.IN_PROGRESS))
    
    archived_count = await archive_past_incomplete_missions()
    assert archived_count == 0
    assert _mock_db_missions[0].status == MissionStatus.NOT_STARTED
    assert _mock_db_missions[1].status == MissionStatus.IN_PROGRESS

@pytest.mark.asyncio
async def test_archive_past_incomplete_missions():
    """Test that past incomplete missions are archived."""
    today_utc7 = get_utc7_today_date()
    yesterday_utc7 = today_utc7 - timedelta(days=1)
    two_days_ago_utc7 = today_utc7 - timedelta(days=2)

    # Missions that should be archived
    _mock_db_missions.append(_create_mission_doc("user1", yesterday_utc7, MissionStatus.NOT_STARTED))
    _mock_db_missions.append(_create_mission_doc("user2", two_days_ago_utc7, MissionStatus.IN_PROGRESS))
    
    # Missions that should NOT be archived
    _mock_db_missions.append(_create_mission_doc("user3", yesterday_utc7, MissionStatus.COMPLETE)) # Already complete
    _mock_db_missions.append(_create_mission_doc("user4", two_days_ago_utc7, MissionStatus.ARCHIVED)) # Already archived
    _mock_db_missions.append(_create_mission_doc("user5", today_utc7, MissionStatus.NOT_STARTED)) # Today's mission

    initial_db_size = len(_mock_db_missions)

    archived_count = await archive_past_incomplete_missions()
    assert archived_count == 2
    assert len(_mock_db_missions) == initial_db_size # No missions deleted

    for mission in _mock_db_missions:
        if mission.user_id == "user1" and mission.date == yesterday_utc7:
            assert mission.status == MissionStatus.ARCHIVED
            assert mission.updated_at.date() == datetime.now(timezone.utc).date()
        elif mission.user_id == "user2" and mission.date == two_days_ago_utc7:
            assert mission.status == MissionStatus.ARCHIVED
            assert mission.updated_at.date() == datetime.now(timezone.utc).date()
        elif mission.user_id == "user3":
            assert mission.status == MissionStatus.COMPLETE
        elif mission.user_id == "user4":
            assert mission.status == MissionStatus.ARCHIVED # Should remain archived
        elif mission.user_id == "user5":
            assert mission.status == MissionStatus.NOT_STARTED

@pytest.mark.asyncio
async def test_archive_all_are_past_incomplete():
    """Test archiving when all missions are past and incomplete."""
    today_utc7 = get_utc7_today_date()
    yesterday_utc7 = today_utc7 - timedelta(days=1)

    _mock_db_missions.append(_create_mission_doc("user1", yesterday_utc7, MissionStatus.NOT_STARTED))
    _mock_db_missions.append(_create_mission_doc("user2", yesterday_utc7, MissionStatus.IN_PROGRESS))
    
    archived_count = await archive_past_incomplete_missions()
    assert archived_count == 2
    assert _mock_db_missions[0].status == MissionStatus.ARCHIVED
    assert _mock_db_missions[1].status == MissionStatus.ARCHIVED

@pytest.mark.asyncio
async def test_archive_mixed_dates_and_statuses():
    """More comprehensive test with mixed scenarios."""
    today_utc7 = get_utc7_today_date()
    d_minus_1 = today_utc7 - timedelta(days=1)
    d_minus_2 = today_utc7 - timedelta(days=2)
    d_minus_3 = today_utc7 - timedelta(days=3)

    # Setup
    _mock_db_missions.extend([
        _create_mission_doc("user_today_ns", today_utc7, MissionStatus.NOT_STARTED),         # No change
        _create_mission_doc("user_past_ns", d_minus_1, MissionStatus.NOT_STARTED),           # Archive
        _create_mission_doc("user_past_ip", d_minus_2, MissionStatus.IN_PROGRESS),         # Archive
        _create_mission_doc("user_past_comp", d_minus_1, MissionStatus.COMPLETE),          # No change
        _create_mission_doc("user_past_arch", d_minus_3, MissionStatus.ARCHIVED),         # No change
        _create_mission_doc("user_deep_past_ns", d_minus_3, MissionStatus.NOT_STARTED),   # Archive
    ])

    archived_count = await archive_past_incomplete_missions()
    assert archived_count == 3

    status_map = { (m.user_id, m.date): m.status for m in _mock_db_missions }

    assert status_map[("user_today_ns", today_utc7)] == MissionStatus.NOT_STARTED
    assert status_map[("user_past_ns", d_minus_1)] == MissionStatus.ARCHIVED
    assert status_map[("user_past_ip", d_minus_2)] == MissionStatus.ARCHIVED
    assert status_map[("user_past_comp", d_minus_1)] == MissionStatus.COMPLETE
    assert status_map[("user_past_arch", d_minus_3)] == MissionStatus.ARCHIVED
    assert status_map[("user_deep_past_ns", d_minus_3)] == MissionStatus.ARCHIVED

    # Verify updated_at was touched for archived missions
    for mission_doc in _mock_db_missions:
        if mission_doc.user_id in ["user_past_ns", "user_past_ip", "user_deep_past_ns"]:
            assert mission_doc.updated_at.date() == datetime.now(timezone.utc).date()
            assert (datetime.now(timezone.utc) - mission_doc.updated_at).total_seconds() < 5 # recent
        else: # For non-archived missions, updated_at should be the old one
             assert mission_doc.updated_at.date() == (datetime.now(timezone.utc) - timedelta(days=10)).date()

if __name__ == '__main__':
    unittest.main() 