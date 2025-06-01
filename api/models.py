from pydantic import BaseModel
from enum import Enum
from typing import TypedDict , Optional


class Priority(str, Enum):
    high = "high"
    low = "low"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    PERMANENTLY_FAILED = "permanently_failed"


class MailRequest(BaseModel):
    job_type: str
    priority: Priority
    payload: str


class ProcessQueryResponse(TypedDict):
    message: str
    query_id: int
    data: dict

class JobMap(BaseModel):
    id: int
    job_type: str
    payload: str
    priority: str
    created_at: float
    picked_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0
    last_error: Optional[str] = None

