from datetime import date, datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.models.daily_mission import DailyMissionDocument, MissionStatus

# Define collection name
MISSIONS_COLLECTION = "missions"

class MissionRepository:
    """
    Handles loading and accessing mission data from a persistent source.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[MISSIONS_COLLECTION]

    async def find_mission(self, user_id: str, mission_date: date) -> Optional[DailyMissionDocument]:
        """
        Finds a mission in the database for a given user and date.
        """
        mission_doc = await self.collection.find_one({
            "user_id": user_id,
            "date": datetime.combine(mission_date, datetime.min.time()) # Store date as datetime object at midnight
        })
        if mission_doc:
            return DailyMissionDocument(**mission_doc)
        return None

    async def save_mission(self, mission_doc: DailyMissionDocument) -> DailyMissionDocument:
        """
        Saves a mission to the database using upsert.
        If a mission with the same user_id and date already exists, it updates it.
        Otherwise, it inserts the new mission.
        """
        # Convert Pydantic model to a dict for MongoDB
        mission_data = mission_doc.model_dump()
        
        # Pydantic's `date` type needs to be a `datetime` in MongoDB for proper queries.
        # We store the date as a datetime at midnight UTC.
        if isinstance(mission_data["date"], date) and not isinstance(mission_data["date"], datetime):
             mission_data["date"] = datetime.combine(mission_data["date"], datetime.min.time())

        await self.collection.update_one(
            {"user_id": mission_doc.user_id, "date": mission_data["date"]},
            {"$set": mission_data},
            upsert=True
        )
        return mission_doc

    async def get_missions_to_archive(self, before_date: date) -> List[DailyMissionDocument]:
        """
        Retrieves all missions before a given date that are not complete or archived.
        """
        # Convert the date to a datetime object at midnight for the query
        before_datetime = datetime.combine(before_date, datetime.min.time())

        cursor = self.collection.find({
            "date": {"$lt": before_datetime},
            "status": {"$nin": [MissionStatus.COMPLETE.value, MissionStatus.ARCHIVED.value]}
        })
        
        # The find method itself returns the cursor, it is not async.
        # It is iterating the cursor that is async.
        # The previous refactoring was incorrect. Reverting to async for.
        missions_to_update: List[DailyMissionDocument] = []
        async for mission_doc in cursor:
            missions_to_update.append(DailyMissionDocument(**mission_doc))
            
        return missions_to_update

    async def clear_all_missions(self):
        """A helper method for testing to clear the in-memory store."""
        await self.collection.delete_many({}) 