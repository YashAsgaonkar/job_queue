from pydantic import BaseModel
from enum import Enum
from typing import TypedDict


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

class QueueItem(BaseModel):
    id: int
    job_type: str
    payload: str
    priority: str
    timestamp: float
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0

class ProcessQueryResponse(TypedDict):
    message: str
    query_id: int
    data: dict
