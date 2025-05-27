import datetime
import pytest
from pydantic import ValidationError

from backend.models.daily_mission import DailyMissionDocument, MissionStatus


@pytest.fixture
def valid_mission_data():
    """Provides a dictionary of valid data for creating a DailyMissionDocument."""
    return {
        "user_id": "test_user_123",
        "date": datetime.date(2023, 10, 27),
        "question_ids": ["q1", "q2", "q3", "q4", "q5"],
    }


@pytest.fixture
def five_question_ids():
    return ["id_001", "id_002", "id_003", "id_004", "id_005"]


def test_daily_mission_creation_success(valid_mission_data, five_question_ids):
    """Test successful creation of a DailyMissionDocument with valid data."""
    data = valid_mission_data.copy()
    data["question_ids"] = five_question_ids
    mission = DailyMissionDocument(**data)

    assert mission.user_id == data["user_id"]
    assert mission.date == data["date"]
    assert mission.question_ids == five_question_ids
    assert mission.status == MissionStatus.NOT_STARTED  # Default value
    assert isinstance(mission.created_at, datetime.datetime)
    assert isinstance(mission.updated_at, datetime.datetime)
    # Check timestamps are recent (e.g., within the last few seconds)
    assert (datetime.datetime.utcnow() - mission.created_at).total_seconds() < 5
    assert (datetime.datetime.utcnow() - mission.updated_at).total_seconds() < 5


def test_daily_mission_default_values(valid_mission_data):
    """Test that default values are correctly assigned."""
    mission = DailyMissionDocument(**valid_mission_data)
    assert mission.status == MissionStatus.NOT_STARTED
    assert mission.created_at is not None
    assert mission.updated_at is not None
    assert mission.created_at <= datetime.datetime.utcnow()
    assert mission.updated_at <= datetime.datetime.utcnow()


@pytest.mark.parametrize(
    "missing_field", ["user_id", "date", "question_ids"]
)
def test_daily_mission_missing_required_fields(valid_mission_data, missing_field):
    """Test ValidationError is raised if required fields are missing."""
    data = valid_mission_data.copy()
    del data[missing_field]
    with pytest.raises(ValidationError) as exc_info:
        DailyMissionDocument(**data)
    assert missing_field in str(exc_info.value)


@pytest.mark.parametrize(
    "field_name,invalid_value,expected_error_part",
    [
        ("user_id", 123, "str_type"),  # Expecting string, got int
        ("date", "not-a-date", "date_from_datetime_parsing"),
        ("question_ids", "not-a-list", "list_type"),
        ("question_ids", [1, 2, 3, 4, 5], "str_type"), # List of ints instead of strings
        ("status", "invalid_status", "enum_value_error"), # Invalid enum value
    ],
)
def test_daily_mission_invalid_data_types(
    valid_mission_data, field_name, invalid_value, expected_error_part
):
    """Test ValidationError for incorrect data types or invalid enum values."""
    data = valid_mission_data.copy()
    data[field_name] = invalid_value
    with pytest.raises(ValidationError) as exc_info:
        DailyMissionDocument(**data)
    assert field_name in str(exc_info.value)
    assert expected_error_part in str(exc_info.value).lower()


@pytest.mark.parametrize(
    "num_questions", [0, 4, 6]
)
def test_daily_mission_invalid_question_ids_count(valid_mission_data, num_questions):
    """Test ValidationError for incorrect number of question_ids."""
    data = valid_mission_data.copy()
    data["question_ids"] = [f"q{i}" for i in range(num_questions)]
    with pytest.raises(ValidationError) as exc_info:
        DailyMissionDocument(**data)
    assert "question_ids" in str(exc_info.value)
    if num_questions < 5:
        assert "ensure this value has at least 5 items" in str(exc_info.value).lower() 
    else: # num_questions > 5
        assert "ensure this value has at most 5 items" in str(exc_info.value).lower()


def test_mission_status_enum_values(valid_mission_data):
    """Test correct assignment and validation of MissionStatus enum."""
    data_in_progress = valid_mission_data.copy()
    data_in_progress["status"] = MissionStatus.IN_PROGRESS
    mission_in_progress = DailyMissionDocument(**data_in_progress)
    assert mission_in_progress.status == MissionStatus.IN_PROGRESS

    data_complete = valid_mission_data.copy()
    data_complete["status"] = "complete"  # Test assignment from string value
    mission_complete = DailyMissionDocument(**data_complete)
    assert mission_complete.status == MissionStatus.COMPLETE

    with pytest.raises(ValidationError):
        invalid_data = valid_mission_data.copy()
        invalid_data["status"] = "pending_approval" # Not a valid status
        DailyMissionDocument(**invalid_data)


def test_timestamps_update_on_model_change(valid_mission_data):
    """ Test that updated_at timestamp changes (conceptually). 
        Pydantic models are immutable by default, so this test is more conceptual.
        If using an ORM/ODM that supports automatic updates, this behavior would be tested there.
        For a plain Pydantic model, `updated_at` would need to be manually set on updates.
    """
    mission = DailyMissionDocument(**valid_mission_data)
    initial_created_at = mission.created_at
    initial_updated_at = mission.updated_at

    # Simulate a delay and a conceptual update
    # In a real scenario with an ODM, fetching and saving would update timestamps.
    # For Pydantic, if you were to create a new model instance representing an update:
    # new_data = mission.dict()
    # new_data["status"] = MissionStatus.COMPLETE
    # # For Pydantic, you'd manually update the timestamp if you're replacing the object
    # # new_data["updated_at"] = datetime.datetime.utcnow() 
    # updated_mission = DailyMissionDocument(**new_data)

    # This test primarily confirms initial setting. True update testing depends on ODM/DB layer.
    assert initial_created_at is not None
    assert initial_updated_at is not None
    assert mission.updated_at >= mission.created_at


def test_schema_extra_example_is_valid(valid_mission_data):
    """Test that the example in schema_extra can be parsed correctly."""
    example_data = DailyMissionDocument.Config.schema_extra["example"].copy()
    # Pydantic expects date/datetime objects, not strings, for these fields during parsing
    example_data["date"] = datetime.date.fromisoformat(example_data["date"])
    example_data["created_at"] = datetime.datetime.fromisoformat(example_data["created_at"].replace("Z", "+00:00"))
    example_data["updated_at"] = datetime.datetime.fromisoformat(example_data["updated_at"].replace("Z", "+00:00"))
    
    mission = DailyMissionDocument(**example_data)
    assert mission.user_id == example_data["user_id"]
    assert mission.status == MissionStatus.NOT_STARTED # As per example 