
def get_score(priority: str, created_at: float) -> float:
    """
    Calculate the score for a job based on its priority and creation time.
    Higher priority jobs get lower scores (higher priority = lower score).
    """
    weight = -1000 if priority == "high" else 0
    return weight + created_at / 1e8

def calculate_backoff(retry_count: int) -> int:
    """Calculate exponential backoff time in seconds"""
    return 2 ** retry_count

