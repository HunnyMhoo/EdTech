import pytest
import asyncio
import os
from pathlib import Path
from unittest.mock import patch

import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from backend.database import db_manager, DatabaseManager
from backend.repositories.question_repository import QuestionRepository
from backend.repositories.mission_repository import MissionRepository

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_db_manager(event_loop):
    """
    Function-scoped fixture to manage the test database connection.
    Connects and disconnects for each test function.
    """
    # Load .env file from the backend directory
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Use a dedicated test database and a fallback URI
    mongo_uri = os.environ.get("MONGO_DB_URI", "mongodb://localhost:27017")
    original_db_name = os.environ.get("MONGO_DB_NAME")
    os.environ["MONGO_DB_NAME"] = "edtech_test"

    # Use a separate DatabaseManager instance for tests
    test_db_manager = DatabaseManager()
    
    # Temporarily set the URI in the environment if it's not already there
    with patch.dict(os.environ, {"MONGO_DB_URI": mongo_uri}):
        test_db_manager.connect_to_database(path_to_env=env_path)
    
    # Yield the manager to the tests
    yield test_db_manager
    
    # Teardown: close connection and restore environment
    test_db_manager.close_database_connection()
    if original_db_name:
        os.environ["MONGO_DB_NAME"] = original_db_name
    else:
        if "MONGO_DB_NAME" in os.environ:
            del os.environ["MONGO_DB_NAME"]

@pytest_asyncio.fixture
async def clean_collections(test_db_manager: DatabaseManager):
    """
    Fixture that cleans the database collections before each test.
    This ensures that tests run in an isolated environment.
    """
    db = test_db_manager.get_database()
    question_repo = QuestionRepository(db)
    mission_repo = MissionRepository(db)
    
    # Clean up collections before the test runs
    await question_repo.clear_all_questions_from_db()
    await mission_repo.clear_all_missions()
    
    yield
    
    # Optional: you could also clean up after the test if needed,
    # but cleaning before is usually sufficient for isolation. 