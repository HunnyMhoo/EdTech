import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Assuming your FastAPI app instance is accessible for TestClient
# This might need adjustment based on your project structure.
# If main.py creates app, you might do: from backend.main import app
# For now, let's assume 'app' is created in a way that questions_router is included.

from fastapi import FastAPI
from backend.routes.questions import router as questions_router
from backend.models.daily_mission import Question, ChoiceOption

# Create a minimal app for testing this specific router
app = FastAPI()
app.include_router(questions_router)

client = TestClient(app)

@pytest.fixture
def sample_question_payload() -> dict:
    return {
        "question_id": "GATQ001",
        "question_text": "What is a cat?",
        "skill_area": "Animals",
        "difficulty_level": 1,
        "feedback_th": "แมวคือสัตว์เลี้ยง",
        "choices": [
            {"id": "a", "text": "A type of dog"},
            {"id": "b", "text": "A furry feline"},
            {"id": "c", "text": "A bird"}
        ],
        "correct_answer_id": "b"
    }

@pytest.fixture
def sample_question_model(sample_question_payload: dict) -> Question:
    return Question(**sample_question_payload)

def test_get_question_by_id_success(sample_question_model: Question, sample_question_payload: dict):
    """Test successfully retrieving a question by its ID."""
    with patch('backend.routes.questions.get_question_details_by_id') as mock_get_details:
        mock_get_details.return_value = sample_question_model
        
        response = client.get(f"/questions/{sample_question_model.question_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Pydantic models stringify enums, convert if necessary for comparison or ensure model output matches
        assert response_data["question_id"] == sample_question_payload["question_id"]
        assert response_data["question_text"] == sample_question_payload["question_text"]
        assert response_data["feedback_th"] == sample_question_payload["feedback_th"]
        assert response_data["choices"] == sample_question_payload["choices"] # Direct comparison for list of dicts
        assert response_data["correct_answer_id"] == sample_question_payload["correct_answer_id"]
        
        mock_get_details.assert_called_once_with(sample_question_model.question_id)

def test_get_question_by_id_not_found():
    """Test retrieving a question that does not exist (404)."""
    non_existent_id = "NONEXISTENT001"
    with patch('backend.routes.questions.get_question_details_by_id') as mock_get_details:
        mock_get_details.return_value = None # Simulate question not found
        
        response = client.get(f"/questions/{non_existent_id}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Question with ID '{non_existent_id}' not found. Ensure the question exists and the CSV data is correctly loaded."
        mock_get_details.assert_called_once_with(non_existent_id)

def test_get_question_by_id_invalid_path_param_type():
    """
    Test FastAPI's automatic validation for path parameter types.
    e.g. if question_id was expected to be an int. Here it's str, so less relevant unless format constraints.
    For this example, if question_id had a regex constraint like ^GATQ[0-9]{3}$, FastAPI would handle it.
    Since it's just a string, any non-empty string is usually accepted by default for path.
    If specific format validation (e.g. via Path(..., regex=...)) was added to the route, this test would be more meaningful.
    Currently, this will likely just pass through to the not_found logic if the string doesn't match an ID.
    """
    # This test is more illustrative. If `question_id` had regex validation in `Path`, this would test rejection.
    # With simple `str` type, it's hard to make it "invalid" at FastAPI's Path level without a regex.
    # It will just be treated as a string ID.
    invalid_format_id = "123-ABC-!" # An ID that might not match a typical format but is still a string
    
    with patch('backend.routes.questions.get_question_details_by_id') as mock_get_details:
        mock_get_details.return_value = None # To ensure it goes to 404 if ID is "valid" string but not found
        
        response = client.get(f"/questions/{invalid_format_id}")
        
        # Expecting 404 because the mocked service function will return None
        assert response.status_code == 404 
        assert response.json()["detail"] == f"Question with ID '{invalid_format_id}' not found. Ensure the question exists and the CSV data is correctly loaded."
        mock_get_details.assert_called_once_with(invalid_format_id)

# To run these tests (from the root directory of your project, assuming pytest is installed):
# Ensure your PYTHONPATH is set up if backend modules are not found, e.g.:
# export PYTHONPATH=.
# pytest backend/tests/integration/test_questions_route.py 