from api.models.models import ProcessQueryResponse, JobMap, JobStatus
from api.utils.redis_client import redis_client
from api.utils.utils import get_score
import time 

async def process_query_controller(query):
    try:
        # Generate unique ID atomically
        query_id = redis_client.incr("query:id:counter")

        # Add extra fields
        queue_item = JobMap(
            id=query_id,
            job_type=query.job_type,
            payload=query.payload,
            priority=query.priority,
            created_at=time.time(),
            status=JobStatus.PENDING,
            retry_count=0
        )

        score = get_score(query.priority, queue_item.created_at)
        # Push to Redis sorted set
        redis_client.zadd("Mail_queue", {queue_item.model_dump_json(): score})
        # Push in map for quick access
        redis_client.hset("Job_map", query_id, queue_item.model_dump_json())

        return ProcessQueryResponse(
            message="Query processed successfully",
            query_id=query_id,
            data=queue_item.model_dump()
        )
    except Exception as e:
        return ProcessQueryResponse(
            message=f"Failed to process query: {str(e)}",
            query_id=None,
            data={}
        )


async def job_status_controller(job_id: int):
    try:
        # Get the status of that job
        job_details = redis_client.hget("Job_map", job_id)
        if not job_details:
            return ProcessQueryResponse(
                message="Job not found or has no logs",
                query_id=job_id,
                data={}
            )
        
        # Decode and send the job details
        job = JobMap.model_validate_json(job_details.decode("utf-8"))
        return ProcessQueryResponse(
            message="Job logs retrieved successfully",
            query_id=job_id,
            data=job
        )
    except Exception as e:
        return ProcessQueryResponse(
            message=f"Failed to retrieve job status: {str(e)}",
            query_id=job_id,
            data={}
        )