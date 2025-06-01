from pydantic import BaseModel
from enum import Enum
from typing import TypedDict


class Priority(str, Enum):
    high = "high"
    low = "low"

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
    status: str = "pending"
    retry_count: int = 0

class ProcessQueryResponse(TypedDict):
    message: str
    query_id: int
    data: dict
