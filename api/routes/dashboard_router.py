from fastapi import APIRouter, HTTPException
from api.utils.redis_client import redis_client
from api.models.models import JobMap, PaginatedTasksResponse
from api.controllers.dashboard_controller import get_paginated_tasks

import json
router = APIRouter()


@router.get("/tasks", response_model=PaginatedTasksResponse)
async def get_tasks(page: int = 1, limit: int = 10):
    """
    Retrieve paginated tasks from the Job_map hash in Redis
    """
    return await get_paginated_tasks(page, limit)