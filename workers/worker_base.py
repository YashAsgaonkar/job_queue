import json
import time
import random
import logging
from typing import Optional
from api.redis_client import redis_client
from api.models import JobMap, JobStatus
from api.utils import get_score

logger = logging.getLogger("job_worker")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class Worker:
    def __init__(self, main_queue: str, retry_queue: str, sleep_time: int = 5):
        self.main_queue = main_queue
        self.retry_queue = retry_queue
        self.sleep_time = sleep_time

    def parse_job_data(self, job_json: bytes) -> JobMap:
        job_dict = json.loads(job_json.decode('utf-8'))
        return JobMap.model_validate(job_dict)

    def update_job_status(self, job_data: JobMap, status: JobStatus, error: Optional[str] = None):
        job_data.status = status
        current_time = time.time()

        if status == JobStatus.PROCESSING:
            job_data.picked_at = current_time
        elif status in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.PERMANENTLY_FAILED]:
            job_data.completed_at = current_time

        if error:
            job_data.last_error = error
            logger.error(f"[Job {job_data.id}] {error}")
        else:
            logger.info(f"[Job {job_data.id}] Status updated to {status}")

        redis_client.hset("Job_map", job_data.id, job_data.model_dump_json())

    def requeue_job(self, job_data: JobMap, queue_name: str):
        score = get_score(job_data.priority, time.time())
        redis_client.zadd(queue_name, {job_data.model_dump_json(): score})
        logger.info(f"[Job {job_data.id}] Re-queued to {queue_name}")

    def process_job(self, job_data: JobMap) -> bool:
        logger.info(f"[Job {job_data.id}] Processing: {job_data.job_type}")
        time.sleep(2)

        if random.random() < 0.4:
            logger.warning(f"[Job {job_data.id}] Failed.")
            return False

        logger.info(f"[Job {job_data.id}] Completed successfully.")
        return True

    def run(self):
        raise NotImplementedError("Subclasses must implement the run method.")
