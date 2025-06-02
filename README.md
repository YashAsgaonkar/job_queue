# Background Processing System

A robust background processing system for handling email tasks with priority queuing, automatic retries, and a visual dashboard for monitoring job status.

## Overview

This system provides a scalable solution for processing mail tasks asynchronously with the following features:

- **Priority Queue System**: Jobs are processed based on priority (high/low)
- **Automatic Retry Mechanism**: Failed jobs are retried with exponential backoff
- **Web Dashboard**: Real-time monitoring with filtering and sorting capabilities
- **RESTful API**: Simple endpoints for job submission and status checking
- **Persistent Storage**: All jobs are stored in Redis for durability
- **Worker Architecture**: Separate workers for main and retry queues

## System Architecture

The system consists of three main components:

1. **API Server** (`api/main.py`): FastAPI application that handles:
   - Job submission via REST endpoints
   - Job status checking
   - Dashboard for monitoring

2. **Main Queue Worker** (`workers/main_worker.py`): 
   - Processes jobs from the main queue
   - Updates job status
   - Moves failed jobs to retry queue

3. **Retry Queue Worker** (`workers/retry_worker.py`):
   - Handles failed jobs with exponential backoff
   - Requeues jobs to the main queue for processing

## Installation

### Prerequisites

- Python 3.8+
- Redis server

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YashAsgaonkar/job_queue.git
   cd mail_bg
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   # Copy the sample.env file
   cp sample.env .env
   
   # Edit .env with your Redis credentials
   # REDIS_HOST=your_host
   # REDIS_PORT=your_port
   # REDIS_PASSWORD=your_password
   ```

## Running the System

### Start the API Server

```bash
python -m api.main
```

This will start the FastAPI server at http://127.0.0.1:8000

### Start the Workers

In separate terminal windows:

```bash
# Start the main queue worker
python -m workers.main_worker

# Start the retry queue worker
python -m workers.retry_worker
```

## API Usage

### Submit a Job

```bash
curl -X POST "http://127.0.0.1:8000/api/process_query" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "send_email",
    "priority": "high",
    "payload": "{\"to\": \"user@example.com\", \"subject\": \"Test Email\", \"message\": \"This is a test email.\"}"
  }'
```

Response:
```json
{
  "message": "Query processed successfully",
  "query_id": 1,
  "data": {
    "id": 1,
    "job_type": "send_email",
    "payload": "{\"to\": \"user@example.com\", \"subject\": \"Test Email\", \"message\": \"This is a test email.\"}",
    "priority": "high",
    "created_at": 1748783995.8422053,
    "picked_at": null,
    "completed_at": null,
    "status": "pending",
    "retry_count": 0,
    "last_error": null
  }
}
```

### Check Job Status

```bash
curl "http://127.0.0.1:8000/api/job/status/1"
```

Response:
```json
{
  "message": "Job logs retrieved successfully",
  "query_id": 1,
  "data": {
    "id": 1,
    "job_type": "send_email",
    "payload": "{\"to\": \"user@example.com\", \"subject\": \"Test Email\", \"message\": \"This is a test email.\"}",
    "priority": "high",
    "created_at": 1748783995.8422053,
    "picked_at": 1748784000.1234567,
    "completed_at": 1748784010.7654321,
    "status": "success",
    "retry_count": 0,
    "last_error": null
  }
}
```

## Web Dashboard

Access the dashboard at http://127.0.0.1:8000/dashboard

![Dashboard Screenshot](api/static/dashboard.jpg)

The dashboard provides:
- Real-time view of all jobs in the system
- Filtering by job status (pending, processing, success, failed, permanently failed)
- Sorting by any column (ID, job type, priority, timestamps, status, retry count)
- Pagination for navigating large job sets
- Detailed view of each job with complete information

## Core Components

### Job Model

Jobs are represented using the `JobMap` model with the following attributes:

- `id`: Unique identifier
- `job_type`: Type of job (e.g., "send_email")
- `payload`: Job data as a JSON string
- `priority`: Priority level (high/low)
- `created_at`: Timestamp when job was created
- `picked_at`: Timestamp when job was picked for processing
- `completed_at`: Timestamp when job processing was completed
- `status`: Current status (pending, processing, success, failed, permanently_failed)
- `retry_count`: Number of retry attempts
- `last_error`: Last error message if any

### Worker System

#### Worker Base Class (`worker_base.py`)

Provides common functionality:
- Job parsing and validation
- Status updates
- Error handling
- Requeuing failed jobs

#### Main Queue Worker (`main_worker.py`)

1. Pulls jobs from the main queue
2. Updates job status to "processing"
3. Executes the job
4. On success, updates status to "success"
5. On failure, increments retry count and moves to retry queue if under max retries

#### Retry Queue Worker (`retry_worker.py`)

1. Pulls jobs from the retry queue
2. Applies exponential backoff based on retry count
3. Requeues jobs to the main queue for processing

## Redis Data Structure

The system uses Redis for storage and queuing:

- `Mail_queue`: Sorted set containing pending jobs (scored by priority and time)
- `Retry_queue`: Sorted set containing failed jobs awaiting retry
- `Job_map`: Hash mapping job IDs to job details for quick lookup
- `query:id:counter`: Counter for generating unique job IDs

## Development

### Project Structure

```
mail_bg/
├── api/                  # API and web server
│   ├── controllers/      # Business logic
│   ├── models/           # Data models
│   ├── routes/           # API endpoints
│   ├── static/           # Dashboard frontend
│   └── utils/            # Utility functions
├── workers/              # Background workers
│   ├── worker_base.py    # Base worker class
│   ├── main_worker.py    # Main queue worker
│   └── retry_worker.py   # Retry queue worker
├── requirements.txt      # Dependencies
└── sample.env            # Environment variables template
```

### Adding New Job Types

To add a new job type:

1. Extend the processing logic in the `process_job` method of the `Worker` class
2. Add appropriate validation for the new job type's payload
3. Submit jobs with the new job type via the API

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.