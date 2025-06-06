import csv
from pathlib import Path
from typing import Dict, Optional, List

# Assuming models are accessible. If not, adjust the import path.
# This might require adding backend/ to PYTHONPATH or using relative imports.
from backend.models.daily_mission import Question, ChoiceOption

class QuestionRepository:
    """
    Handles loading and accessing question data from a persistent source (e.g., CSV).
    """
    _questions_cache: Dict[str, Question] = {}
    _is_initialized: bool = False

    def __init__(self, questions_csv_path: Path):
        self.questions_csv_path = questions_csv_path

    def _initialize_cache(self):
        """Loads all question details from the CSV file into an in-memory cache."""
        if not self.questions_csv_path.exists():
            raise FileNotFoundError(f"Question file not found: {self.questions_csv_path}")
        
        try:
            with open(self.questions_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if not reader.fieldnames:
                    # Consider logging this instead of raising an exception that could halt the app
                    print(f"Warning: CSV file {self.questions_csv_path} is empty or has no headers.")
                    return

                for row_num, row in enumerate(reader, start=2):
                    question_id = row.get('question_id')
                    if not question_id:
                        print(f"Warning: Skipping row {row_num} due to missing question_id.")
                        continue

                    try:
                        # Parse choices
                        parsed_choices: List[ChoiceOption] = []
                        for i in range(1, 5): # Assuming up to 4 choices
                            choice_id = row.get(f'choice_{i}_id')
                            choice_text = row.get(f'choice_{i}_text')
                            if choice_id and choice_text:
                                parsed_choices.append(ChoiceOption(id=choice_id, text=choice_text))

                        correct_answer_id = row.get('correct_answer_id')
                        if correct_answer_id and not any(c.id == correct_answer_id for c in parsed_choices):
                            print(f"Warning: correct_answer_id '{correct_answer_id}' for question '{question_id}' does not match any choice IDs.")
                            correct_answer_id = None
                        
                        question = Question(
                            question_id=question_id,
                            question_text=row.get('question_text', ''),
                            skill_area=row.get('skill_area', 'N/A'),
                            difficulty_level=int(row.get('difficulty_level', 0) or 0),
                            feedback_th=row.get('feedback_th', ''),
                            choices=parsed_choices,
                            correct_answer_id=correct_answer_id
                        )
                        self._questions_cache[question.question_id] = question
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Skipping question_id '{question_id}' due to data conversion error: {e}")
            
            self._is_initialized = True
            print(f"Successfully loaded {len(self._questions_cache)} questions into cache from {self.questions_csv_path}.")

        except Exception as e:
            # In a production system, you'd use a robust logger
            print(f"CRITICAL: Failed to load question file {self.questions_csv_path}: {e}")
            # Depending on requirements, you might re-raise or let the app run with no questions
            raise

    def get_all_questions(self) -> Dict[str, Question]:
        """Returns all questions, initializing the cache if necessary."""
        if not self._is_initialized:
            self._initialize_cache()
        return self._questions_cache

    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Retrieves a single question by its ID."""
        if not self._is_initialized:
            self._initialize_cache()
        return self._questions_cache.get(question_id)

# --- Singleton Instance ---
# For simplicity in this refactoring, we'll create a single, shared instance.
# In a larger application, dependency injection would be preferred.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QUESTIONS_FILE_PATH = DATA_DIR / "gat_questions.csv"

question_repository = QuestionRepository(QUESTIONS_FILE_PATH) 