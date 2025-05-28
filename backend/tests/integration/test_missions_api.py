from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from unittest.mock import patch, AsyncMock # For mocking service calls and dependencies

from backend.routes.missions import router as missions_router, get_current_user_id
from backend.services.mission_service import DailyMission as DailyMissionSchema # Import the Pydantic model
from backend.models.api_responses import MissionResponse # Import the response model
from datetime import datetime, timezone, timedelta

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


@patch("backend.routes.missions.get_todays_mission_for_user", new_callable=AsyncMock)
def test_get_today_mission_success(mock_get_todays_mission):
    """Test successful retrieval of today's mission."""
    # Configure the mock service function to return a sample mission
    sample_mission_date = FIXED_DATETIME_NOW.astimezone(UTC7_TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    mock_mission_data = DailyMissionSchema(
        userId=MOCK_USER_ID,
        date=sample_mission_date, # Date should be UTC representation of UTC+7 start of day
        questionIds=["q1", "q2", "q3", "q4", "q5"],
        status="not_started",
        createdAt=FIXED_DATETIME_NOW
    )
    mock_get_todays_mission.return_value = mock_mission_data

    response = client.get("/api/missions/today")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["message"] == "Today's mission retrieved successfully."
    assert response_data["data"]["userId"] == MOCK_USER_ID
    assert response_data["data"]["questionIds"] == ["q1", "q2", "q3", "q4", "q5"]
    # FastAPI serializes datetime to ISO 8601 string format.
    # We need to compare the date part carefully or parse it back if exact time is important.
    # For 'date' field, it represents start of day. For 'createdAt', it's a timestamp.
    assert response_data["data"]["date"] == mock_mission_data.date.isoformat().replace("+00:00", "Z")
    assert response_data["data"]["createdAt"] == mock_mission_data.createdAt.isoformat().replace("+00:00", "Z")

    mock_get_todays_mission.assert_called_once_with(MOCK_USER_ID)

@patch("backend.routes.missions.get_todays_mission_for_user", new_callable=AsyncMock)
def test_get_today_mission_not_found(mock_get_todays_mission):
    """Test when no mission is found for today."""
    # Configure the mock service function to return None (mission not found)
    mock_get_todays_mission.return_value = None

    response = client.get("/api/missions/today")

    assert response.status_code == 404
    response_data = response.json() # FastAPI provides a default JSON body for HTTPException
    assert response_data["detail"] == f"No mission found for user {MOCK_USER_ID} for today (UTC+7)."
    
    mock_get_todays_mission.assert_called_once_with(MOCK_USER_ID)

@patch("backend.routes.missions.get_todays_mission_for_user", new_callable=AsyncMock)
def test_get_today_mission_service_exception(mock_get_todays_mission):
    """Test when the service layer raises an unexpected exception."""
    # Configure the mock service function to raise a generic exception
    test_exception_message = "Service layer exploded!"
    mock_get_todays_mission.side_effect = Exception(test_exception_message)

    response = client.get("/api/missions/today")

    assert response.status_code == 500
    response_data = response.json()
    assert response_data["detail"] == f"An unexpected error occurred: {test_exception_message}"

    mock_get_todays_mission.assert_called_once_with(MOCK_USER_ID)

# To run these tests (assuming pytest and httpx are installed):
# Ensure PYTHONPATH includes the project root or backend directory if needed.
# Example: PYTHONPATH=. pytest backend/tests/integration/test_missions_api.py 