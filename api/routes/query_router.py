from fastapi import APIRouter
from api.utils.redis_client import redis_client
from api.models.models import MailRequest
from api.controllers.query_controller import process_query_controller, job_status_controller

router = APIRouter()

@router.post("/process_query")
async def process_query(query: MailRequest):
    """
    Process a query and push it in queue.
    """
    return await process_query_controller(query)


@router.get("/job/status/{job_id}")
async def job_status(job_id: int):
    """
    Get the status of a job by its ID.
    """
    return await job_status_controller(job_id)



