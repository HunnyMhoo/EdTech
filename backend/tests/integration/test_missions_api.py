import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from unittest.mock import patch, AsyncMock # For mocking service calls and dependencies
from datetime import datetime, timezone, timedelta

from backend.routes.missions import router as missions_router, get_current_user_id
from backend.models.daily_mission import DailyMissionDocument as DailyMissionSchema, Question
from backend.models.api_responses import MissionResponse # Import the response model
from backend.services.mission_service import _mock_db_missions

# Create a FastAPI instance for testing and include the router
app = FastAPI()
app.include_router(missions_router, prefix="/api")

# Create a TestClient
client = TestClient(app)

# Define a fixed datetime for consistent testing, matching service layer logic
FIXED_DATETIME_NOW = datetime(2023, 10, 26, 10, 0, 0, tzinfo=timezone.utc) 
# This will be UTC+7 17:00:00. The date part is what matters for "today".
UTC7_TIMEZONE = timezone(timedelta(hours=7))

# Mock user ID that will be returned by the overridden dependency
MOCK_USER_ID = "test_user_123_integration"

# Override the get_current_user_id dependency for testing
async def override_get_current_user_id() -> str:
    return MOCK_USER_ID

app.dependency_overrides[get_current_user_id] = override_get_current_user_id

@pytest.fixture()
def mock_mission_service():
    """Fixture to mock the mission service functions."""
    with patch("backend.routes.missions.get_todays_mission_for_user", new_callable=AsyncMock) as mock_get_mission:
        yield mock_get_mission

def create_mock_question(question_id: str) -> Question:
    """Helper function to create a mock Question object."""
    return Question(
        question_id=question_id,
        question_text=f"This is a sample question text for {question_id}.",
        skill_area="Testing",
        difficulty_level=1,
    )

@pytest.mark.usefixtures("mock_mission_service")
def test_get_today_mission_success(mock_mission_service):
    """Test successful retrieval of today's mission."""
    sample_mission_date = FIXED_DATETIME_NOW.astimezone(UTC7_TIMEZONE).date()
    mock_questions = [create_mock_question(f"q{i}") for i in range(1, 6)]
    
    mock_mission_data = DailyMissionSchema(
        user_id=MOCK_USER_ID,
        date=sample_mission_date,
        questions=mock_questions,
        status="not_started",
        created_at=FIXED_DATETIME_NOW
    )
    mock_mission_service.return_value = mock_mission_data

    response = client.get("/missions/today")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["message"] == "Today's mission retrieved successfully."
    
    # Validate the structure of the returned mission data
    returned_data = response_data["data"]
    assert returned_data["user_id"] == MOCK_USER_ID
    assert returned_data["date"] == sample_mission_date.isoformat()
    assert len(returned_data["questions"]) == 5
    assert returned_data["questions"][0]["question_id"] == "q1"

    mock_mission_service.assert_called_once_with(MOCK_USER_ID)

@pytest.mark.usefixtures("mock_mission_service")
def test_get_today_mission_not_found(mock_mission_service):
    """Test when no mission is found for today."""
    mock_mission_service.return_value = None

    response = client.get("/missions/today")

    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == f"No mission found for user {MOCK_USER_ID} for today (UTC+7)."
    
    mock_mission_service.assert_called_once_with(MOCK_USER_ID)

@pytest.mark.usefixtures("mock_mission_service")
def test_get_today_mission_service_exception(mock_mission_service):
    """Test when the service layer raises an unexpected exception."""
    test_exception_message = "Service layer exploded!"
    mock_mission_service.side_effect = Exception(test_exception_message)

    response = client.get("/missions/today")

    assert response.status_code == 500
    response_data = response.json()
    assert response_data["detail"] == f"An unexpected error occurred: {test_exception_message}"

    mock_mission_service.assert_called_once_with(MOCK_USER_ID)

# To run these tests (assuming pytest and httpx are installed):
# Ensure PYTHONPATH includes the project root or backend directory if needed.
# Example: PYTHONPATH=. pytest backend/tests/integration/test_missions_api.py 