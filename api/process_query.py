from fastapi import APIRouter
from api.redis_client import redis_client
from api.models import MailRequest, QueueItem, ProcessQueryResponse, JobStatus
import time
import json

router = APIRouter()

@router.post("/process_query")
async def process_query(query: MailRequest):
    """
    Process a query and push it in queue.
    """

    # Generate unique ID atomically
    query_id = redis_client.incr("query:id:counter")

    # Add extra fields
    queue_item = QueueItem(
        id=query_id,
        job_type=query.job_type,
        payload=query.payload,
        priority=query.priority,
        timestamp=time.time(),
        status=JobStatus.PENDING,
        retry_count=0
    )

    # Score: negative priority (so high priority = lower score), then timestamp
    # This ensures high priority comes first, then earlier requests
    weight = -1000 if query.priority == "high" else 0
    score = weight + queue_item.timestamp / 1e8 

    # Push to Redis sorted set
    redis_client.zadd("Mail_queue", {queue_item.model_dump_json(): score})
    # Push to data logs
    redis_client.lpush("Mail_logs", queue_item.model_dump_json())
    # Push in map for quick access
    redis_client.hset("Job_map", query_id, queue_item.model_dump_json())

    return ProcessQueryResponse(
        message="Query processed successfully",
        query_id=query_id,
        data=queue_item.model_dump()
    )

@router.get("/job/status/{job_id}")
async def job_status(job_id: int):
    """
    Get the status of a job by its ID.
    """
    
    # Get the status of that job
    job_details = redis_client.hget("Job_map", job_id)
    if not job_details:
        return ProcessQueryResponse(
            message="Job not found or has no logs",
            query_id=job_id,
            data={}
        )
    
    # Decode and send the job details
    job_dict = json.loads(job_details.decode("utf-8"))
    return ProcessQueryResponse(
        message="Job logs retrieved successfully",
        query_id=job_id,
        data=job_dict
    )

