from fastapi import APIRouter, HTTPException
from api.redis_client import redis_client
from api.models import JobMap
import json
router = APIRouter()

@router.get("/tasks")
async def get_tasks():
    """
    Retrieve all tasks from the Job_map hash in Redis
    """
    try:
        # Get all tasks from the Job_map hash
        tasks_raw = redis_client.hvals("Job_map")
        
        # Parse JSON strings into objects
        tasks = []
        for task_raw in tasks_raw:
            task_data = json.loads(task_raw)
            task = JobMap.model_validate(task_data)
            tasks.append(task.model_dump())
            
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tasks: {str(e)}")
