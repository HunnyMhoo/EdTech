"""
This module defines dependency providers for the application.

Using FastAPI's dependency injection system, these functions provide instances
of repositories or other services to the application's components (e.g., routes, services).
This approach decouples components, making them easier to test and maintain.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends

from backend.repositories.question_repository import QuestionRepository
from backend.repositories.mission_repository import MissionRepository
from backend.database import db_manager


def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get the database instance."""
    return db_manager.get_database()


def get_question_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> QuestionRepository:
    """
    Dependency provider for the QuestionRepository.
    
    Initializes the repository with the database connection and returns an
    instance that caches question data.
    """
    return QuestionRepository(db)


def get_mission_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> MissionRepository:
    """
    Dependency provider for the MissionRepository.

    Initializes the repository with the database connection, providing
    an interface for mission data operations.
    """
    return MissionRepository(db) 