import csv
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Assuming models are accessible. If not, adjust the import path.
# This might require adding backend/ to PYTHONPATH or using relative imports.
from backend.models.daily_mission import Question, ChoiceOption

# Define collection name
QUESTIONS_COLLECTION = "questions"

class QuestionRepository:
    """
    Handles loading and accessing question data from a persistent source (e.g., CSV).
    """
    _questions_cache: Dict[str, Question] = {}
    _is_initialized: bool = False

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[QUESTIONS_COLLECTION]
        self.questions_csv_path = Path(__file__).resolve().parent.parent / "data" / "gat_questions.csv"

    async def _initialize_if_needed(self):
        """
        Initializes the repository by seeding the DB from CSV if empty,
        then loading all questions into the in-memory cache.
        """
        if not self._is_initialized:
            # Check if the collection is empty.
            if await self.collection.count_documents({}) == 0:
                print(f"'{QUESTIONS_COLLECTION}' collection is empty. Seeding from CSV...")
                await self._seed_db_from_csv()
            
            # Load all questions from DB into cache.
            await self._load_cache_from_db()

            self._is_initialized = True
            print(f"Successfully loaded {len(self._questions_cache)} questions into cache from database.")

    async def _load_cache_from_db(self):
        """Loads all questions from the MongoDB collection into the in-memory cache."""
        cursor = self.collection.find({})
        async for question_doc in cursor:
            # Pydantic models can be created directly from the dictionary-like documents
            # returned by Motor, but we need to handle the '_id' field from MongoDB.
            question_doc.pop('_id', None) 
            question = Question(**question_doc)
            self._questions_cache[question.question_id] = question

    async def _seed_db_from_csv(self):
        """
        Reads question data from the CSV file and inserts it into the database.
        This is intended to be a one-time setup operation.
        """
        if not self.questions_csv_path.exists():
            raise FileNotFoundError(f"Question CSV file not found: {self.questions_csv_path}")

        questions_to_insert = []
        try:
            with open(self.questions_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if not reader.fieldnames:
                    print(f"Warning: CSV file {self.questions_csv_path} is empty.")
                    return

                for row_num, row in enumerate(reader, start=2):
                    question_id = row.get('question_id')
                    if not question_id:
                        print(f"Warning: Skipping row {row_num} in CSV due to missing question_id.")
                        continue
                    
                    try:
                        # This logic mirrors the original implementation for consistency
                        parsed_choices: List[dict] = []
                        for i in range(1, 5):
                            choice_id = row.get(f'choice_{i}_id')
                            choice_text = row.get(f'choice_{i}_text')
                            if choice_id and choice_text:
                                parsed_choices.append(ChoiceOption(id=choice_id, text=choice_text).model_dump())

                        question_data = Question(
                            question_id=question_id,
                            question_text=row.get('question_text', ''),
                            skill_area=row.get('skill_area', 'N/A'),
                            difficulty_level=int(row.get('difficulty_level', 0) or 0),
                            feedback_th=row.get('feedback_th', ''),
                            choices=parsed_choices,
                            correct_answer_id=row.get('correct_answer_id')
                        ).model_dump()
                        
                        questions_to_insert.append(question_data)

                    except (ValueError, TypeError) as e:
                        print(f"Warning: Skipping question_id '{question_id}' due to data conversion error: {e}")
            
            if questions_to_insert:
                await self.collection.insert_many(questions_to_insert)
                print(f"Successfully inserted {len(questions_to_insert)} questions into the database.")

        except Exception as e:
            print(f"CRITICAL: Failed to seed question data from {self.questions_csv_path}: {e}")
            raise

    async def get_all_questions(self) -> Dict[str, Question]:
        """Returns all questions, initializing the repository if necessary."""
        await self._initialize_if_needed()
        return self._questions_cache

    async def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Retrieves a single question by its ID from the cache."""
        await self._initialize_if_needed()
        return self._questions_cache.get(question_id)

    async def clear_all_questions_from_db(self):
        """A helper method for testing to clear the questions collection in the DB."""
        await self.collection.delete_many({})
        self._questions_cache.clear()
        self._is_initialized = False
        print("Cleared all questions from the database and reset the cache.")

# --- Singleton Instance Removal ---
# The singleton `question_repository` instance is no longer created here.
# Instances are now created and managed via the dependency injection system. 