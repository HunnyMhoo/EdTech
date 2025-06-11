from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.models.practice_session import PracticeSession, PracticeSessionStatus

# Define collection name
PRACTICE_SESSIONS_COLLECTION = "practice_sessions"

class PracticeRepository:
    """
    Handles loading and accessing practice session data from a persistent source.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[PRACTICE_SESSIONS_COLLECTION]

    async def create_session(self, session: PracticeSession) -> PracticeSession:
        """
        Creates a new practice session in the database.
        """
        session_data = session.model_dump()
        await self.collection.insert_one(session_data)
        return session

    async def find_session(self, session_id: str) -> Optional[PracticeSession]:
        """
        Finds a practice session by its ID.
        """
        session_doc = await self.collection.find_one({"session_id": session_id})
        if session_doc:
            session_doc.pop('_id', None)  # Remove MongoDB's _id field
            return PracticeSession(**session_doc)
        return None

    async def update_session(self, session: PracticeSession) -> PracticeSession:
        """
        Updates an existing practice session.
        """
        session_data = session.model_dump()
        await self.collection.update_one(
            {"session_id": session.session_id},
            {"$set": session_data}
        )
        return session

    async def get_user_sessions(
        self, 
        user_id: str, 
        status: Optional[PracticeSessionStatus] = None,
        limit: int = 50
    ) -> List[PracticeSession]:
        """
        Gets practice sessions for a user, optionally filtered by status.
        """
        query = {"user_id": user_id}
        if status:
            query["status"] = status.value

        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        sessions = []
        
        async for session_doc in cursor:
            session_doc.pop('_id', None)
            sessions.append(PracticeSession(**session_doc))
        
        return sessions

    async def get_user_stats(self, user_id: str) -> dict:
        """
        Gets aggregated statistics for a user's practice sessions.
        """
        pipeline = [
            {"$match": {"user_id": user_id, "status": "completed"}},
            {"$group": {
                "_id": None,
                "total_sessions": {"$sum": 1},
                "total_questions": {"$sum": "$question_count"},
                "total_correct": {"$sum": "$correct_count"},
                "topics_practiced": {"$addToSet": "$topic"}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            return {
                "total_sessions": stats.get("total_sessions", 0),
                "total_questions": stats.get("total_questions", 0),
                "total_correct": stats.get("total_correct", 0),
                "accuracy": (stats.get("total_correct", 0) / stats.get("total_questions", 1)) * 100,
                "topics_practiced": stats.get("topics_practiced", [])
            }
        
        return {
            "total_sessions": 0,
            "total_questions": 0,
            "total_correct": 0,
            "accuracy": 0,
            "topics_practiced": []
        }

    async def delete_session(self, session_id: str) -> bool:
        """
        Deletes a practice session.
        """
        result = await self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    async def cleanup_abandoned_sessions(self, hours_old: int = 24) -> int:
        """
        Cleans up abandoned sessions older than specified hours.
        """
        cutoff_time = datetime.utcnow() - datetime.timedelta(hours=hours_old)
        result = await self.collection.delete_many({
            "status": "in_progress",
            "created_at": {"$lt": cutoff_time}
        })
        return result.deleted_count 