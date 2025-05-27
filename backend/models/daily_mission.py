import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

# It is assumed that if you are using an ODM like Beanie,
# you would import PydanticObjectId from beanie or a similar construct
# for fields that are MongoDB ObjectIds. For this example,
# we are using basic types like str for IDs.


class MissionStatus(str, Enum):
    """
    Represents the completion status of a daily mission.
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DailyMissionDocument(BaseModel):
    """
    Pydantic model representing the schema for a user's daily mission
    stored in MongoDB.
    """
    user_id: str = Field(..., description="The unique identifier for the user.")
    date: datetime.date = Field(..., description="The calendar date for which this mission is assigned (YYYY-MM-DD).")
    question_ids: List[str] = Field(
        ...,
        description="A list of question identifiers that make up the mission.",
        min_items=5,
        max_items=5  # Assuming a fixed number of 5 questions per mission as per User Story 1.1
    )
    status: MissionStatus = Field(
        default=MissionStatus.NOT_STARTED,
        description="The current completion status of the mission."
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Timestamp of when the mission record was created (UTC)."
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Timestamp of when the mission record was last updated (UTC)."
    )

    class Config:
        # Example of how to configure Pydantic to use enum values
        use_enum_values = True
        # If you need to ensure that the model can be used with ORMs or ODMs
        # that expect arbitrary types to be allowed for model attributes,
        # you might set arbitrary_types_allowed = True,
        # but it's generally better to ensure types are well-defined.
        # arbitrary_types_allowed = True

        # Example of schema extras for OpenAPI generation if using FastAPI
        schema_extra = {
            "example": {
                "user_id": "user_123_abc",
                "date": "2023-10-27",
                "question_ids": ["q1", "q2", "q3", "q4", "q5"],
                "status": "not_started",
                "created_at": "2023-10-27T10:00:00.000Z",
                "updated_at": "2023-10-27T10:00:00.000Z",
            }
        }

# Note on Indexing:
# The requirement "Index userId + date to prevent duplicates" needs to be implemented
# at the database level.
# If using BeanieODM, you would add something like this to the DailyMissionDocument class:
#
# class Settings:
#     indexes = [
#         [("user_id", pymongo.ASCENDING), ("date", pymongo.ASCENDING), {"unique": True}]
#     ]
#
# If using Motor directly with Pydantic, this index would typically be created
# as part of your application's startup logic or a database migration script, e.g.:
#
# async def create_indexes(db_collection):
#     await db_collection.create_index(
#         [("user_id", 1), ("date", 1)],
#         unique=True,
#         name="user_date_unique_idx"
#     )
#
# This file defines the Pydantic model. The actual index creation
# depends on the chosen database interaction library (e.g., BeanieODM, Motor). 