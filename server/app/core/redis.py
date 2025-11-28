import redis.asyncio as redis
import json
from typing import Optional, List
from .config import settings


class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def close(self):
        if self.redis:
            await self.redis.close()
    
    # 会话上下文缓存
    async def get_chat_context(self, user_id: int, conversation_id: int, limit: int = 10) -> List[dict]:
        key = f"chat:context:{user_id}:{conversation_id}"
        data = await self.redis.lrange(key, -limit, -1)
        return [json.loads(item) for item in data]
    
    async def add_chat_message(self, user_id: int, conversation_id: int, message: dict):
        key = f"chat:context:{user_id}:{conversation_id}"
        await self.redis.rpush(key, json.dumps(message, ensure_ascii=False))
        await self.redis.ltrim(key, -20, -1)  # 只保留最近20条
        await self.redis.expire(key, 3600)  # 1小时过期
    
    async def clear_chat_context(self, user_id: int, conversation_id: int):
        key = f"chat:context:{user_id}:{conversation_id}"
        await self.redis.delete(key)
    
    # 通用缓存
    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = 300):
        await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        await self.redis.delete(key)

    # 列表操作（用于监控消息）
    async def lrange(self, key: str, start: int, end: int):
        return await self.redis.lrange(key, start, end)

    async def lpush(self, key: str, *values):
        return await self.redis.lpush(key, *values)

    async def ltrim(self, key: str, start: int, end: int):
        return await self.redis.ltrim(key, start, end)


redis_client = RedisClient()
