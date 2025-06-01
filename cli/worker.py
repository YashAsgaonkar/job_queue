import json
import time
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from api.redis_client import redis_client
from api.models import JobStatus,JobMap
from api.utils import get_score



def process_job(job_data: JobMap) -> bool:
    """
    Mock email sending process.
    Returns True if successful, False if failed
    """
    id = job_data.id
    print(f"Processing job {id}: {job_data.job_type}")
    
    # Simulate processing time
    time.sleep(2)
    
    # Simulate random failures (40% chance)
    if random.random() < 0.4:
        print(f"Job {id} failed!")
        
        return False
    
    print(f"Job {id} completed successfully!")
    return True


def update_job_status(job_data: JobMap, status: JobStatus, error: str = None):
    """Update job status in Redis"""
    job_data.status = status
    if status == JobStatus.PROCESSING:
        job_data.picked_at = time.time()
    elif status in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.PERMANENTLY_FAILED]:
        job_data.completed_at = time.time()
    
    if error:
        job_data.last_error = error
    
    # Update in Job_map
    job_json = job_data.model_dump_json()
    redis_client.hset("Job_map", job_data.id, job_json)

def process_queue(sleep_time: int = 5):
    print("Starting job worker...")
    
    while True:
        # Get highest priority job
        result = redis_client.zrange("Mail_queue", 0, 0)
        
        if not result:
            print("Queue is empty. Waiting...")
            time.sleep(sleep_time)
            continue
        
        # Parse job data and ensure type safety
        job_json = result[0].decode('utf-8')
        job_dict = json.loads(job_json)
                
        # Create JobMap object with validation
        job_data = JobMap.model_validate(job_dict)
        
        # Update status to processing
        update_job_status(job_data, JobStatus.PROCESSING)
        
        # Try to process the job
        success = process_job(job_data)
        redis_client.zrem("Mail_queue", job_json)
        if success:
            # Job completed successfully
            update_job_status(job_data, JobStatus.SUCCESS)
            # Remove from queue
        else:
            # Job failed, increment retry count
            job_data.retry_count += 1
            if job_data.retry_count >= 3:
                # Permanently failed after 3 retries
                update_job_status(job_data, JobStatus.PERMANENTLY_FAILED, "Job permanently failed after 3 retries")
            else:
                # Move to retry queue
                update_job_status(job_data, JobStatus.FAILED, "Job failed, moving to retry queue")
                score = get_score(job_data.priority, time.time())
                redis_client.zadd("Retry_queue", {job_data.model_dump_json(): score})
            print(f"Job {job_data.id} moved to retry queue")
        redis_client.hset("Job_map", job_data.id, job_data.model_dump_json())

if __name__ == "__main__":
    try:
        process_queue(10)
    except KeyboardInterrupt:
        print("\nWorker stopped.")