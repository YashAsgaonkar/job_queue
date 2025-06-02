from api.utils.redis_client import redis_client
from api.models.models import JobMap, PaginatedTasksResponse
from fastapi import HTTPException
import json

async def get_paginated_tasks(page: int = 1, limit: int = 10):
    """
    Retrieve paginated tasks from the Job_map hash in Redis
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
        
        # Implement pagination
        total_tasks = len(tasks)
        start = (page - 1) * limit
        end = start + limit
        paginated_tasks = tasks[start:end]
        
        # Return response with metadata
        return PaginatedTasksResponse(
            status="success",
            total_tasks=total_tasks,
            page=page,
            limit=limit,
            tasks_returned=len(paginated_tasks),
            tasks=paginated_tasks
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve tasks: {str(e)}"
        )