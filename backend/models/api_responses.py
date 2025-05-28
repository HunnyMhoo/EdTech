from pydantic import BaseModel
from typing import Optional, Any, TypeVar, Generic, List

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