import json
from api.utils.redis_client import redis_client

# Get the item with the lowest score (highest priority)
result = redis_client.zrange("Mail_queue", 0, 0)

if result:
    # result[0] is a bytes object, decode and load as JSON
    item_json = result[0].decode("utf-8")
    print("Next item in queue:", item_json)
    # Optionally, convert to dict
    item_dict = json.loads(item_json)
    print("As dict:", item_dict)
else:
    print("Queue is empty.")