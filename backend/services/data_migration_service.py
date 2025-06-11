"""
Data Migration Service

Handles migration of existing mission data from legacy answer format 
to new enhanced Answer model with attempt tracking.
"""

from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.models.daily_mission import DailyMissionDocument, Answer, AnswerAttempt
from backend.services.utils import get_current_time_in_target_timezone

class DataMigrationService:
    """Service for migrating legacy mission data to new format."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.missions_collection = db["missions"]
    
    async def migrate_mission_answers(self) -> Dict[str, Any]:
        """
        Migrates all missions with legacy answer format to new Answer model.
        
        Returns:
            Migration summary with statistics
        """
        migrated_count = 0
        error_count = 0
        total_processed = 0
        
        print("Starting mission answer data migration...")
        
        cursor = self.missions_collection.find({})
        
        async for mission_doc in cursor:
            total_processed += 1
            
            try:
                # Check if migration is needed
                if self._needs_migration(mission_doc):
                    await self._migrate_single_mission(mission_doc)
                    migrated_count += 1
                    print(f"Migrated mission for user {mission_doc.get('user_id')} date {mission_doc.get('date')}")
                
            except Exception as e:
                error_count += 1
                print(f"Error migrating mission {mission_doc.get('_id')}: {str(e)}")
        
        summary = {
            "total_processed": total_processed,
            "migrated_count": migrated_count,
            "error_count": error_count,
            "timestamp": get_current_time_in_target_timezone().isoformat()
        }
        
        print(f"Migration completed: {summary}")
        return summary
    
    def _needs_migration(self, mission_doc: Dict[str, Any]) -> bool:
        """
        Checks if a mission document needs migration.
        
        Args:
            mission_doc: Raw mission document from database
            
        Returns:
            True if migration is needed, False otherwise
        """
        answers = mission_doc.get("answers", [])
        
        if not answers:
            return False
        
        # Check if any answer has the old format (missing current_answer field)
        for answer in answers:
            if isinstance(answer, dict):
                # Old format has 'answer' field but not 'current_answer'
                if "answer" in answer and "current_answer" not in answer:
                    return True
                # Also check if required new fields are missing
                if "attempt_count" not in answer or "is_complete" not in answer:
                    return True
        
        return False
    
    async def _migrate_single_mission(self, mission_doc: Dict[str, Any]) -> None:
        """
        Migrates a single mission document to new format.
        
        Args:
            mission_doc: Raw mission document from database
        """
        answers = mission_doc.get("answers", [])
        migrated_answers = []
        
        for answer_data in answers:
            if isinstance(answer_data, dict):
                migrated_answer = self._convert_answer_format(answer_data)
                migrated_answers.append(migrated_answer)
        
        # Update the mission document
        mission_doc["answers"] = migrated_answers
        mission_doc["updated_at"] = get_current_time_in_target_timezone()
        
        # Save back to database
        await self.missions_collection.replace_one(
            {"_id": mission_doc["_id"]},
            mission_doc
        )
    
    def _convert_answer_format(self, old_answer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts old answer format to new Answer model format.
        
        Args:
            old_answer: Answer in legacy format
            
        Returns:
            Answer in new format compatible with Answer model
        """
        # Extract old format fields
        question_id = old_answer.get("question_id", "")
        old_answer_value = old_answer.get("answer", "")
        feedback_shown = old_answer.get("feedback_shown", False)
        
        # Create attempt history from the old answer
        attempt_history = []
        if old_answer_value:  # Only create attempt if there was an answer
            attempt = {
                "answer": old_answer_value,
                "is_correct": old_answer.get("is_correct", False),
                "timestamp": old_answer.get("timestamp", datetime.utcnow())
            }
            attempt_history.append(attempt)
        
        # Create new format answer
        new_answer = {
            "question_id": question_id,
            "current_answer": old_answer_value,
            "is_correct": old_answer.get("is_correct", False),
            "attempt_count": 1 if old_answer_value else 0,
            "attempts_history": attempt_history,
            "feedback_shown": feedback_shown,
            "is_complete": old_answer.get("is_complete", feedback_shown),  # Complete if feedback was shown
            "max_retries": 3
        }
        
        return new_answer
    
    async def validate_migration(self) -> Dict[str, Any]:
        """
        Validates that all missions have been properly migrated.
        
        Returns:
            Validation summary
        """
        total_missions = 0
        valid_missions = 0
        invalid_missions = []
        
        cursor = self.missions_collection.find({})
        
        async for mission_doc in cursor:
            total_missions += 1
            
            try:
                # Try to parse with new model
                DailyMissionDocument(**mission_doc)
                valid_missions += 1
            except Exception as e:
                invalid_missions.append({
                    "mission_id": str(mission_doc.get("_id")),
                    "user_id": mission_doc.get("user_id"),
                    "error": str(e)
                })
        
        validation_summary = {
            "total_missions": total_missions,
            "valid_missions": valid_missions,
            "invalid_missions_count": len(invalid_missions),
            "invalid_missions": invalid_missions[:5],  # Show first 5 errors
            "validation_passed": len(invalid_missions) == 0
        }
        
        return validation_summary

# Utility function for easy migration execution
async def run_migration(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """
    Convenience function to run the complete migration process.
    
    Args:
        db: Database connection
        
    Returns:
        Combined migration and validation results
    """
    migration_service = DataMigrationService(db)
    
    print("=== Starting Data Migration ===")
    migration_result = await migration_service.migrate_mission_answers()
    
    print("\n=== Validating Migration ===")
    validation_result = await migration_service.validate_migration()
    
    return {
        "migration": migration_result,
        "validation": validation_result
    } 