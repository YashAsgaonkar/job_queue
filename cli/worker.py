import json
import time
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from api.redis_client import redis_client
from api.models import JobStatus



def process_job(job_data: dict) -> bool:
    """
    Mock email sending process.
    Returns True if successful, False if failed
    """
    print(f"Processing job {job_data['id']}: {job_data['job_type']}")
    
    # Simulate processing time
    time.sleep(2)
    
    # Simulate random failures (20% chance)
    if random.random() < 0.2:
        print(f"Job {job_data['id']} failed!")
        return False
    
    print(f"Job {job_data['id']} completed successfully!")
    return True

def calculate_backoff(retry_count: int) -> int:
    """Calculate exponential backoff time in seconds"""
    return 2 ** retry_count

def update_job_status(job_data: dict, status: JobStatus, error: str = None):
    """Update job status in Redis"""
    job_data['status'] = status
    if status == JobStatus.PROCESSING:
        job_data['picked_at'] = time.time()
    elif status in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.PERMANENTLY_FAILED]:
        job_data['completed_at'] = time.time()
    
    if error:
        job_data['last_error'] = error
    
    # Update in Job_map
    redis_client.hset("Job_map", job_data['id'], json.dumps(job_data))

def process_queue():
    print("Starting job worker...")
    
    while True:
        # Get highest priority job
        result = redis_client.zrange("Mail_queue", 0, 0)
        
        if not result:
            print("Queue is empty. Waiting...")
            time.sleep(5)
            continue
        
        # Parse job data
        job_json = result[0].decode('utf-8')
        job_data = json.loads(job_json)
        
        # Update status to processing
        update_job_status(job_data, JobStatus.PROCESSING)
        
        # Try to process the job
        success = process_job(job_data)
        
        if success:
            # Job completed successfully
            update_job_status(job_data, JobStatus.SUCCESS)
            # Remove from queue
            redis_client.zrem("Mail_queue", job_json)
        else:
            # Handle failure
            job_data['retry_count'] += 1
            
            if job_data['retry_count'] >= 3:
                # Mark as permanently failed
                update_job_status(job_data, JobStatus.PERMANENTLY_FAILED, 
                                "Max retry attempts reached")
                redis_client.zrem("Mail_queue", job_json)
            else:
                # Update for retry
                update_job_status(job_data, JobStatus.FAILED, 
                                f"Failed attempt {job_data['retry_count']}")
                
                # Calculate new score with backoff
                backoff = calculate_backoff(job_data['retry_count'])
                new_score = time.time() + backoff
                
                # Remove old entry and add back with new score
                redis_client.zrem("Mail_queue", job_json)
                redis_client.zadd("Mail_queue", {json.dumps(job_data): new_score})
                
                print(f"Job {job_data['id']} will retry in {backoff} seconds")

if __name__ == "__main__":
    try:
        process_queue()
    except KeyboardInterrupt:
        print("\nWorker stopped.")