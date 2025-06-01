import time
from workers.worker_base import Worker
from api.redis_client import redis_client
from api.models import JobStatus
from api.utils import calculate_backoff


class RetryQueueWorker(Worker):
    def run(self):
        logger = self.__class__.__name__
        print(f"{logger} started...")

        while True:
            result = redis_client.zrange(self.retry_queue, 0, 0)
            if not result:
                print("Retry queue empty. Waiting...")
                time.sleep(self.sleep_time)
                continue

            job_data = self.parse_job_data(result[0])
            redis_client.zrem(self.retry_queue, result[0])

            backoff = calculate_backoff(job_data.retry_count)
            print(f"[Job {job_data.id}] Waiting {backoff}s before requeue.")
            time.sleep(backoff)

            job_data.status = JobStatus.PENDING
            self.requeue_job(job_data, self.main_queue)


if __name__ == "__main__":
    try:
        worker = RetryQueueWorker("Mail_queue", "Retry_queue", sleep_time=5)
        worker.run()
    except KeyboardInterrupt:
        print("Retry worker stopped.")
