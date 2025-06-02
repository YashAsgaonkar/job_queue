from pydantic import BaseModel
from enum import Enum
from typing import TypedDict , Optional, List


class Priority(str, Enum):
    high = "high"
    low = "low"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    PERMANENTLY_FAILED = "permanently_failed"

class JobMap(BaseModel):
    id: int
    job_type: str
    payload: str
    priority: Priority
    created_at: float
    picked_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0
    last_error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "job_type": "send_email",
                "payload": "{'to': 'user@example.com', 'subject': 'Test', 'message': 'Hello!'}",
                "priority": "high",
                "created_at": 1748783995.8422053,
                "picked_at": None,
                "completed_at": None,
                "status": "pending",
                "retry_count": 0,
                "last_error": None
            }
        }


class MailRequest(BaseModel):
    job_type: str
    priority: Priority
    payload: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_type": "send_email",
                "priority": "high",
                "payload": "{'to': 'hello@gmail.com', 'subject': 'Test Email', 'message': 'This is a test email.'}"
            }
        }

class PaginatedTasksResponse(BaseModel):
    status: str
    total_tasks: int
    page: int
    limit: int
    tasks_returned: int
    tasks: List[JobMap]  # List of JobMap objects

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "total_tasks": 100,
                "page": 1,
                "limit": 10,
                "tasks_returned": 10,
                "tasks": [
                    {
                        "id": 1,
                        "job_type": "send_email",
                        "payload": "{'to': 'user@example.com', 'subject': 'Test', 'message': 'Hello!'}",
                        "priority": "high",
                        "created_at": 1748783995.8422053,
                        "picked_at": None,
                        "completed_at": None,
                        "status": "pending",
                        "retry_count": 0,
                        "last_error": None
                    },
                    {
                        "id": 2,
                        "job_type": "send_email",
                        "payload": "{'to': 'user@example.com', 'subject': 'Test', 'message': 'Hello!'}",
                        "priority": "low",
                        "created_at": 1748783996.8422053,
                        "picked_at": 1748784000.1234567,
                        "completed_at": 1748784010.7654321,
                        "status": "success",
                        "retry_count": 0,
                        "last_error": None
                    }
                ]
            }
        }


class ProcessQueryResponse(TypedDict):
    message: str
    query_id: int
    data: JobMap

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Query processed successfully",
                "query_id": 1,
                "data": {
                    "id": 1,
                    "job_type": "send_email",
                    "payload": "{'to': 'hello@123,com', 'subject': 'Test Email', 'message': 'This is a test email.'}",
                    "priority": "high",
                    "created_at": 1748783995.8422053,
                    "picked_at": None,
                    "completed_at": None,
                    "status": "pending",
                    "retry_count": 0,
                    "last_error": None
                }
            }
        }


