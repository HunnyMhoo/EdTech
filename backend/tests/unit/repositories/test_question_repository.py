import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from backend.models.daily_mission import Question, ChoiceOption
from backend.repositories.question_repository import QuestionRepository

@pytest.fixture
def mock_db_collection():
    """Fixture to create a mock database collection."""
    mock_collection = AsyncMock()
    mock_collection.count_documents.return_value = 0
    mock_collection.find.return_value = []
    return mock_collection

@pytest.fixture
def mock_db(mock_db_collection):
    """Fixture to create a mock database."""
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_db_collection
    return mock_db

@pytest.fixture
def question_repository(mock_db):
    """Fixture to create a QuestionRepository instance with a mock database."""
    return QuestionRepository(db=mock_db)

@pytest.mark.asyncio
async def test_initialization_with_empty_db_and_no_csv(question_repository, mock_db_collection):
    """
    Tests that initialization with an empty database and no CSV file to seed from
    results in a FileNotFoundError.
    """
    with patch.object(Path, 'exists') as mock_exists:
        mock_exists.return_value = False
        with pytest.raises(FileNotFoundError):
            await question_repository._initialize_if_needed()

@pytest.mark.asyncio
async def test_get_all_questions_initializes_and_returns_cache(question_repository, mock_db_collection):
    """
    Tests that get_all_questions triggers initialization and returns the (initially empty) cache.
    """
    assert not question_repository._is_initialized

    # Patch _initialize_if_needed and make it set the flag
    async def mock_init_side_effect(*args, **kwargs):
        question_repository._questions_cache = {} # Simulate cache loading
        question_repository._is_initialized = True

    with patch.object(QuestionRepository, '_initialize_if_needed', new_callable=AsyncMock, side_effect=mock_init_side_effect) as mock_init:
        result = await question_repository.get_all_questions()
        mock_init.assert_called_once()
        assert result == {}
        assert question_repository._is_initialized

@pytest.mark.asyncio
async def test_initialization_is_skipped_if_already_initialized(question_repository, mock_db_collection):
    """
    Tests that the expensive DB seeding and cache loading is skipped if the repo is already initialized.
    """
    question_repository._is_initialized = True
    
    # We spy on the internal methods that should NOT be called.
    with patch.object(question_repository, '_seed_db_from_csv', new_callable=AsyncMock) as mock_seed_db, \
         patch.object(question_repository, '_load_cache_from_db', new_callable=AsyncMock) as mock_load_cache:

        # Call a public method that triggers initialization
        await question_repository.get_all_questions()

        # Assert that the core initialization logic was skipped
        mock_seed_db.assert_not_called()
        mock_load_cache.assert_not_called()

@pytest.mark.asyncio
async def test_get_question_by_id_returns_question_from_cache(question_repository):
    """
    Tests that get_question_by_id returns a question from the cache after initialization.
    """
    question_id = "q1"
    question = Question(question_id=question_id, question_text="Test?", skill_area="math", difficulty_level=1, choices=[], correct_answer_id="c1", feedback_th="Good job")
    
    # Manually set up the cache and initialized state
    question_repository._questions_cache[question_id] = question
    question_repository._is_initialized = True

    # Call the method
    result = await question_repository.get_question_by_id(question_id)
    
    # Assert result is correct
    assert result == question

@pytest.mark.asyncio
async def test_get_question_by_id_not_found(question_repository):
    """
    Tests that get_question_by_id returns None for a non-existent question.
    """
    question_repository._is_initialized = True # Pretend it is initialized
    result = await question_repository.get_question_by_id("non_existent_id")
    assert result is None 