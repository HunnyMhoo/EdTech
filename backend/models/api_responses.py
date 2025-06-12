from pydantic import BaseModel
from typing import Optional, Any, TypeVar, Generic, List, Dict
from datetime import date, datetime

# Define a generic type variable
DataType = TypeVar('DataType')

class MissionResponse(BaseModel, Generic[DataType]):
    status: str  # e.g., "success", "error", "not_found"
    data: Optional[DataType] = None
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: Optional[str] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[List[ErrorDetail]] = None

class ReviewMistakeItem(BaseModel):
    question_id: str
    question_text: str
    skill_area: str
    difficulty_level: int
    choices: List[Dict[str, str]]  # [{"id": "choice_id", "text": "choice_text"}]
    user_answer_id: str
    user_answer_text: str
    correct_answer_id: str
    correct_answer_text: str
    explanation: str
    mission_date: date
    mission_completion_date: datetime
    attempt_count: int

class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_previous: bool

class ReviewMistakesResponse(BaseModel):
    mistakes: List[ReviewMistakeItem]
    pagination: PaginationInfo
    total_mistakes: int

class GroupedReviewMistakesResponse(BaseModel):
    grouped_mistakes: Dict[str, List[ReviewMistakeItem]]  # key is either date string or skill_area
    pagination: PaginationInfo
    total_mistakes: int
    group_counts: Dict[str, int]  # count per group 