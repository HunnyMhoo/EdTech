import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from backend.services.practice_service import (
    create_practice_session,
    get_practice_session,
    submit_practice_answer,
    get_practice_session_summary,
    get_available_practice_topics,
    PracticeServiceError,
    InsufficientQuestionsError,
    SessionNotFoundError,
    SessionAlreadyCompletedError,
)
from backend.models.practice_session import PracticeSession, PracticeSessionStatus
from backend.models.daily_mission import Question, ChoiceOption

# Sample test data
@pytest.fixture
def sample_question():
    return Question(
        question_id="test_q1",
        question_text="What is 2+2?",
        skill_area="Math",
        difficulty_level=1,
        choices=[
            ChoiceOption(id="a", text="3"),
            ChoiceOption(id="b", text="4"),
            ChoiceOption(id="c", text="5")
        ],
        correct_answer_id="b",
        feedback_th="2+2 = 4 เป็นการบวกพื้นฐาน"
    )

@pytest.fixture
def sample_questions(sample_question):
    questions = []
    for i in range(5):
        q = Question(
            question_id=f"test_q{i+1}",
            question_text=f"Test question {i+1}",
            skill_area="Math",
            difficulty_level=1,
            choices=[
                ChoiceOption(id="a", text="Option A"),
                ChoiceOption(id="b", text="Option B"),
                ChoiceOption(id="c", text="Option C")
            ],
            correct_answer_id="b",
            feedback_th=f"Test feedback {i+1}"
        )
        questions.append(q)
    return questions

@pytest.fixture
def mock_question_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def mock_practice_repo():
    repo = AsyncMock()
    return repo

@pytest.mark.asyncio
async def test_create_practice_session_success(mock_question_repo, mock_practice_repo, sample_questions):
    """Test successful practice session creation."""
    # Setup mocks
    mock_question_repo.get_topic_question_count.return_value = 10
    mock_question_repo.get_questions_by_topic.return_value = sample_questions
    mock_practice_repo.create_session.return_value = None
    
    # Test session creation
    session = await create_practice_session(
        user_id="test_user",
        topic="Math",
        question_count=5,
        question_repo=mock_question_repo,
        practice_repo=mock_practice_repo
    )
    
    # Assertions
    assert session.user_id == "test_user"
    assert session.topic == "Math"
    assert session.question_count == 5
    assert len(session.questions) == 5
    assert session.status == PracticeSessionStatus.IN_PROGRESS
    
    # Verify repository calls
    mock_question_repo.get_topic_question_count.assert_called_once_with("Math")
    mock_question_repo.get_questions_by_topic.assert_called_once_with("Math", 5)
    mock_practice_repo.create_session.assert_called_once()

@pytest.mark.asyncio
async def test_create_practice_session_insufficient_questions(mock_question_repo, mock_practice_repo):
    """Test practice session creation with insufficient questions."""
    # Setup mocks
    mock_question_repo.get_topic_question_count.return_value = 3
    
    # Test should raise InsufficientQuestionsError
    with pytest.raises(InsufficientQuestionsError) as exc_info:
        await create_practice_session(
            user_id="test_user",
            topic="Math",
            question_count=5,
            question_repo=mock_question_repo,
            practice_repo=mock_practice_repo
        )
    
    assert "only has 3 questions" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_practice_session_invalid_count(mock_question_repo, mock_practice_repo):
    """Test practice session creation with invalid question count."""
    # Test with count too high
    with pytest.raises(PracticeServiceError) as exc_info:
        await create_practice_session(
            user_id="test_user",
            topic="Math",
            question_count=25,
            question_repo=mock_question_repo,
            practice_repo=mock_practice_repo
        )
    
    assert "between 1 and 20" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_practice_session_success(mock_practice_repo, sample_questions):
    """Test successful practice session retrieval."""
    # Setup mock
    session = PracticeSession(
        user_id="test_user",
        topic="Math",
        question_count=5,
        questions=sample_questions
    )
    mock_practice_repo.find_session.return_value = session
    
    # Test session retrieval
    result = await get_practice_session("session_123", mock_practice_repo)
    
    # Assertions
    assert result == session
    mock_practice_repo.find_session.assert_called_once_with("session_123")

@pytest.mark.asyncio
async def test_get_practice_session_not_found(mock_practice_repo):
    """Test practice session retrieval when session not found."""
    # Setup mock
    mock_practice_repo.find_session.return_value = None
    
    # Test should raise SessionNotFoundError
    with pytest.raises(SessionNotFoundError) as exc_info:
        await get_practice_session("session_123", mock_practice_repo)
    
    assert "not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_submit_practice_answer_correct(mock_practice_repo, sample_questions):
    """Test submitting a correct answer."""
    # Setup session
    session = PracticeSession(
        user_id="test_user",
        topic="Math",
        question_count=5,
        questions=sample_questions
    )
    mock_practice_repo.find_session.return_value = session
    mock_practice_repo.update_session.return_value = session
    
    # Test answer submission
    feedback = await submit_practice_answer(
        session_id="session_123",
        question_id="test_q1",
        user_answer="b",
        practice_repo=mock_practice_repo
    )
    
    # Assertions
    assert feedback["already_answered"] == False
    assert feedback["is_correct"] == True
    assert feedback["correct_answer"] == "b"
    assert "explanation" in feedback
    assert len(session.answers) == 1
    assert session.answers[0].is_correct == True

@pytest.mark.asyncio
async def test_submit_practice_answer_incorrect(mock_practice_repo, sample_questions):
    """Test submitting an incorrect answer."""
    # Setup session
    session = PracticeSession(
        user_id="test_user",
        topic="Math",
        question_count=5,
        questions=sample_questions
    )
    mock_practice_repo.find_session.return_value = session
    mock_practice_repo.update_session.return_value = session
    
    # Test answer submission
    feedback = await submit_practice_answer(
        session_id="session_123",
        question_id="test_q1",
        user_answer="a",
        practice_repo=mock_practice_repo
    )
    
    # Assertions
    assert feedback["already_answered"] == False
    assert feedback["is_correct"] == False
    assert feedback["correct_answer"] == "b"
    assert len(session.answers) == 1
    assert session.answers[0].is_correct == False

@pytest.mark.asyncio
async def test_submit_practice_answer_session_complete(mock_practice_repo, sample_questions):
    """Test submitting answer that completes the session."""
    # Setup session with 1 question
    session = PracticeSession(
        user_id="test_user",
        topic="Math",
        question_count=1,
        questions=[sample_questions[0]]
    )
    mock_practice_repo.find_session.return_value = session
    mock_practice_repo.update_session.return_value = session
    
    # Test answer submission
    feedback = await submit_practice_answer(
        session_id="session_123",
        question_id="test_q1",
        user_answer="b",
        practice_repo=mock_practice_repo
    )
    
    # Assertions
    assert feedback["session_complete"] == True
    assert session.status == PracticeSessionStatus.COMPLETED
    assert session.completed_at is not None

@pytest.mark.asyncio
async def test_get_available_practice_topics(mock_question_repo):
    """Test getting available practice topics."""
    # Setup mocks
    mock_question_repo.get_available_topics.return_value = ["Math", "Reading", "Logic"]
    mock_question_repo.get_topic_question_count.side_effect = [10, 15, 8]
    
    # Test topic retrieval
    topics = await get_available_practice_topics(mock_question_repo)
    
    # Assertions
    assert len(topics) == 3
    assert topics[0]["name"] == "Math"
    assert topics[0]["question_count"] == 10
    assert topics[0]["available"] == True
    assert topics[1]["name"] == "Reading"
    assert topics[1]["question_count"] == 15
    assert topics[1]["available"] == True

@pytest.mark.asyncio
async def test_get_practice_session_summary(mock_practice_repo, sample_questions):
    """Test getting practice session summary."""
    # Setup completed session
    session = PracticeSession(
        user_id="test_user",
        topic="Math",
        question_count=5,
        questions=sample_questions,
        status=PracticeSessionStatus.COMPLETED,
        correct_count=3
    )
    session.completed_at = datetime.utcnow()
    
    # Add some answers
    from backend.models.practice_session import PracticeAnswer
    session.answers = [
        PracticeAnswer(question_id="test_q1", user_answer="b", is_correct=True),
        PracticeAnswer(question_id="test_q2", user_answer="a", is_correct=False),
        PracticeAnswer(question_id="test_q3", user_answer="b", is_correct=True),
    ]
    
    mock_practice_repo.find_session.return_value = session
    
    # Test summary retrieval
    summary = await get_practice_session_summary("session_123", mock_practice_repo)
    
    # Assertions
    assert summary["session_id"] == session.session_id
    assert summary["topic"] == "Math"
    assert summary["status"] == "completed"
    assert summary["correct_answers"] == 3
    assert "score" in summary
    assert summary["score"]["total_questions"] == 5 