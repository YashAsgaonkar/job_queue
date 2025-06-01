import redis
import os
from dotenv import load_dotenv
load_dotenv()
redis_host = os.getenv("REDIS_HOST", None)
redis_port = os.getenv("REDIS_PORT", 6379)
redis_password = os.getenv("REDIS_PASSWORD", None)

if not redis_host:
    raise ValueError("Redis host not set. Please set the REDIS_HOST environment variable.")
if not redis_password:
    raise ValueError("Redis password not set. Please set the REDIS_PASSWORD environment variable.")

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    ssl=True
)
