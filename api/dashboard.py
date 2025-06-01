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

@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """
    Retrieve a specific task by ID
    """
    try:
        # Get task from hash map for quick access
        task_raw = redis_client.hget("Job_map", task_id)
        
        if not task_raw:
            raise HTTPException(
            status_code=404, 
            detail=f"Task {task_id} not found"
            )
        task_data = json.loads(task_raw)
        task = JobMap.model_validate(task_data)
        return task.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve task: {str(e)}")