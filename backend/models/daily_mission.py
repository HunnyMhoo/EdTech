import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class MissionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ARCHIVED = "archived"

class ChoiceOption(BaseModel):
    id: str = Field(default_factory=lambda: f"choice_{uuid.uuid4().hex}")
    text: str

class Question(BaseModel):
    question_id: str = Field(default_factory=lambda: f"GATQ_{uuid.uuid4().hex[:6].upper()}")
    question_text: str
    skill_area: str
    difficulty_level: int
    choices: List[ChoiceOption]
    correct_answer_id: str
    feedback_th: str

class DailyMissionDocument(BaseModel):
    user_id: str
    date: date
    questions: List[Question]
    status: MissionStatus = MissionStatus.NOT_STARTED
    current_question_index: int = 0
    answers: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True 