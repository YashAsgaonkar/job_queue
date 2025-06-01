import json
import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from api.redis_client import redis_client
from api.models import JobMap,JobStatus
from api.utils import get_score, calculate_backoff

def process_retry_queue(sleep_time: int = 5):
    print("Starting retry worker...")
    while True:
        result = redis_client.zrange("Retry_queue", 0, 0)
        if not result:
            print("Retry queue is empty. Waiting...")
            time.sleep(5)
            continue
        
        # Parse job data
        job_json = result[0].decode('utf-8')
        job_dict = json.loads(job_json)
        # Create JobMap object with validation
        job_data = JobMap.model_validate(job_dict)
        retry_count = job_data.retry_count
        backoff_time = calculate_backoff(retry_count)
        # Remove job from retry queue
        redis_client.zrem("Retry_queue", result[0])
        # Wait for backoff time before re-queueing
        print(f"Waiting for {backoff_time} seconds before re-queueing job {job_data.id}...")
        time.sleep(backoff_time)
        # Insert job back into main queue (assuming main queue is 'Job_queue')
        score = get_score(job_data.priority, time.time())
        job_data.status = JobStatus.PENDING
        redis_client.zadd("Mail_queue", {job_data.model_dump_json(): score})
        print(f"Job {job_data.id} re-queued to mail queue.")


if __name__ == "__main__":
    try:
        process_retry_queue()
    except KeyboardInterrupt:
        print("\nRetry worker stopped.")