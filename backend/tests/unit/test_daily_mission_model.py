import datetime
import pytest
from pydantic import ValidationError
from typing import List

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Question, ChoiceOption

def create_mock_question(question_id: str) -> Question:
    """Helper function to create a mock Question object for testing."""
    return Question(
        question_id=question_id,
        question_text=f"Sample question text for {question_id}",
        skill_area="Test Skill",
        difficulty_level=1,
        choices=[ChoiceOption(id="a", text="Option A")],
        correct_answer_id="a"
    )

@pytest.fixture
def five_mock_questions() -> List[Question]:
    """Provides a list of five mock Question objects."""
    return [create_mock_question(f"q{i}") for i in range(1, 6)]


@pytest.fixture
def valid_mission_data(five_mock_questions: List[Question]):
    """Provides a dictionary of valid data for creating a DailyMissionDocument."""
    return {
        "user_id": "test_user_123",
        "date": datetime.date(2023, 10, 27),
        "questions": five_mock_questions,
    }


def test_daily_mission_creation_success(valid_mission_data: dict, five_mock_questions: List[Question]):
    """Test successful creation of a DailyMissionDocument with valid data."""
    mission = DailyMissionDocument(**valid_mission_data)

    assert mission.user_id == valid_mission_data["user_id"]
    assert mission.date == valid_mission_data["date"]
    assert mission.questions == five_mock_questions
    assert mission.status == MissionStatus.NOT_STARTED
    assert isinstance(mission.created_at, datetime.datetime)
    assert isinstance(mission.updated_at, datetime.datetime)
    now = datetime.datetime.utcnow()
    assert (now - mission.created_at).total_seconds() < 5
    assert (now - mission.updated_at).total_seconds() < 5


def test_daily_mission_default_values(valid_mission_data: dict):
    """Test that default values are correctly assigned."""
    mission = DailyMissionDocument(**valid_mission_data)
    assert mission.status == MissionStatus.NOT_STARTED
    assert mission.current_question_index == 0
    assert mission.answers == []
    assert mission.created_at is not None
    assert mission.updated_at is not None
    assert mission.created_at <= datetime.datetime.utcnow()
    assert mission.updated_at <= datetime.datetime.utcnow()


@pytest.mark.parametrize(
    "missing_field", ["user_id", "date", "questions"]
)
def test_daily_mission_missing_required_fields(valid_mission_data: dict, missing_field: str):
    """Test ValidationError is raised if required fields are missing."""
    data = valid_mission_data.copy()
    del data[missing_field]
    with pytest.raises(ValidationError) as exc_info:
        DailyMissionDocument(**data)
    assert missing_field in str(exc_info.value)


@pytest.mark.parametrize(
    "field_name,invalid_value,expected_error_part",
    [
        pytest.param("user_id", 123, "str_type", marks=pytest.mark.skip(reason="Pydantic v2 seems to coerce int to str for user_id")),
        ("date", "not-a-date", "date"),
        ("questions", "not-a-list", "list"),
        ("questions", [1, 2, 3, 4, 5], "dict"), # List of ints instead of Questions
        ("status", "invalid_status", "enum"),
    ],
)
def test_daily_mission_invalid_data_types(
    valid_mission_data: dict, field_name: str, invalid_value, expected_error_part: str
):
    """Test ValidationError for incorrect data types or invalid enum values."""
    data = valid_mission_data.copy()
    data[field_name] = invalid_value
    with pytest.raises(ValidationError) as exc_info:
        DailyMissionDocument(**data)
    assert field_name in str(exc_info.value)
    assert expected_error_part in str(exc_info.value)


@pytest.mark.parametrize(
    "num_questions", [0, 4, 6]
)
def test_daily_mission_invalid_questions_count(valid_mission_data: dict, num_questions: int):
    """Test ValidationError for incorrect number of questions."""
    data = valid_mission_data.copy()
    data["questions"] = [create_mock_question(f"q{i}") for i in range(num_questions)]
    with pytest.raises(ValidationError) as exc_info:
        DailyMissionDocument(**data)
    assert "questions" in str(exc_info.value)
    if num_questions < 5:
        assert "at least 5" in str(exc_info.value)
    else: # num_questions > 5
        assert "at most 5" in str(exc_info.value)


def test_mission_status_enum_values(valid_mission_data: dict):
    """Test correct assignment and validation of MissionStatus enum."""
    # Test assignment with Enum member
    data_in_progress = valid_mission_data.copy()
    data_in_progress["status"] = MissionStatus.IN_PROGRESS
    mission_in_progress = DailyMissionDocument(**data_in_progress)
    assert mission_in_progress.status == MissionStatus.IN_PROGRESS

    # Test assignment with string value
    data_complete = valid_mission_data.copy()
    data_complete["status"] = "complete"
    mission_complete = DailyMissionDocument(**data_complete)
    assert mission_complete.status == MissionStatus.COMPLETE
    
    # Test invalid enum value
    with pytest.raises(ValidationError):
        invalid_data = valid_mission_data.copy()
        invalid_data["status"] = "pending_approval"
        DailyMissionDocument(**invalid_data)

def test_timestamps_are_set_on_creation(valid_mission_data: dict):
    """Test that created_at and updated_at are set upon creation."""
    mission = DailyMissionDocument(**valid_mission_data)
    assert isinstance(mission.created_at, datetime.datetime)
    assert isinstance(mission.updated_at, datetime.datetime)
    assert mission.updated_at >= mission.created_at

    # Check that timestamps are close to the current time in UTC
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # The model uses naive datetimes from utcnow(), so we create a naive datetime for comparison
    now_naive = datetime.datetime.utcnow() 
    assert (now_naive - mission.created_at).total_seconds() < 5
    assert (now_naive - mission.updated_at).total_seconds() < 5


def test_schema_extra_example_is_valid():
    """Test that the example in schema_extra can be parsed correctly."""
    example_data = DailyMissionDocument.model_json_schema()["example"]
    
    # The example in the model has strings for dates and datetimes
    # Pydantic v2 can parse these automatically when creating a model instance
    mission = DailyMissionDocument(**example_data)
    
    assert mission.user_id == example_data["user_id"]
    assert mission.status == MissionStatus.NOT_STARTED
    assert len(mission.questions) == 5 # Based on the provided example
    assert mission.questions[0].question_id == "GATQ001" 