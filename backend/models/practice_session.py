import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from enum import Enum

from .daily_mission import Question

class PracticeSessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class PracticeAnswer(BaseModel):
    """Answer model for practice sessions - simplified version without retry logic"""
    question_id: str
    user_answer: Any
    is_correct: bool
    answered_at: datetime = Field(default_factory=datetime.utcnow)

class PracticeSession(BaseModel):
    """
    Practice session model for free practice mode.
    Independent from daily missions and doesn't affect user progress.
    """
    session_id: str = Field(default_factory=lambda: f"PRACTICE_{uuid.uuid4().hex[:8].upper()}")
    user_id: str
    topic: str  # Maps to skill_area in questions
    question_count: int
    questions: List[Question]
    answers: List[PracticeAnswer] = Field(default_factory=list)
    status: PracticeSessionStatus = PracticeSessionStatus.IN_PROGRESS
    correct_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        use_enum_values = True

    def calculate_score(self) -> dict:
        """Calculate session score and statistics"""
        total_questions = len(self.questions)
        answered_questions = len(self.answers)
        correct_answers = sum(1 for answer in self.answers if answer.is_correct)
        
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "correct_answers": correct_answers,
            "accuracy": (correct_answers / answered_questions * 100) if answered_questions > 0 else 0,
            "completion_rate": (answered_questions / total_questions * 100) if total_questions > 0 else 0
        }

    def is_complete(self) -> bool:
        """Check if all questions have been answered"""
        return len(self.answers) >= len(self.questions)

    def mark_completed(self):
        """Mark session as completed and set completion time"""
        self.status = PracticeSessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.correct_count = sum(1 for answer in self.answers if answer.is_correct) 