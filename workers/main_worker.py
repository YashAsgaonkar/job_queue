from workers.worker_base import Worker
from api.models.models import JobStatus
from api.utils.redis_client import redis_client
import time

class MainQueueWorker(Worker):
    def run(self):
        logger = self.__class__.__name__
        print(f"{logger} started...")

        while True:
            result = redis_client.zrange(self.main_queue, 0, 0)
            if not result:
                print("Main queue empty. Waiting...")
                time.sleep(self.sleep_time)
                continue

            job_data = self.parse_job_data(result[0])
            redis_client.zrem(self.main_queue, result[0])

            self.update_job_status(job_data, JobStatus.PROCESSING)
            success = self.process_job(job_data)

            if success:
                self.update_job_status(job_data, JobStatus.SUCCESS)
            else:
                job_data.retry_count += 1
                if job_data.retry_count > 3:
                    self.update_job_status(job_data, JobStatus.PERMANENTLY_FAILED, "Job permanently failed after 3 retries")
                else:
                    self.update_job_status(job_data, JobStatus.FAILED, "Job failed, moving to retry queue")
                    self.requeue_job(job_data, self.retry_queue)


if __name__ == "__main__":
    try:
        worker = MainQueueWorker("Mail_queue", "Retry_queue", sleep_time=10)
        worker.run()
    except KeyboardInterrupt:
        print("Main worker stopped.")
