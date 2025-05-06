import redis.asyncio as redis

from meilisync.enums import ProgressType
from meilisync.progress import Progress
from loguru import logger

class Redis(Progress):
    type = ProgressType.redis

    def __init__(
        self,
        dsn: str = "redis://localhost:6379/0",
        key: str = "meilisync:progress",
    ):
        super().__init__(dsn=dsn, key=key)
        self.key = key
        self.redis = redis.from_url(
            dsn,
            decode_responses=True,
            health_check_interval=30,  # Regularly check connection health
            retry_on_timeout=True      # Auto-retry on timeout
        )

    async def set(self, **kwargs):
        if kwargs:  # Only call hmset if there are actually key-value pairs to set
            try:
                await self.redis.hmset(self.key, kwargs)
            except redis.RedisError as e:
                logger.error(f"Failed to update progress in Redis: {e}")

    async def get(self):
        try:
            return await self.redis.hgetall(self.key)
        except redis.RedisError as e:
            logger.error(f"Failed to retrieve progress from Redis: {e}")
            return {}  # Return empty dict on error or re-raise
