import pytest
import asyncio
from unittest.mock import MagicMock, patch
from app.services.news_scheduler import NewsScheduler, MemoryLock, RedisLock
from app.config import settings

@pytest.mark.asyncio
async def test_scheduler_fallback_no_redis():
    """Test that scheduler starts with MemoryLock when REDIS_URL is None."""
    
    # Mock settings to have no REDIS_URL
    with patch.object(settings, 'redis_url', None):
        # Mock APScheduler to prevent actual scheduling
        with patch('app.services.news_scheduler.AsyncIOScheduler') as MockScheduler:
            mock_scheduler_instance = MagicMock()
            MockScheduler.return_value = mock_scheduler_instance
            
            # Start scheduler
            try:
                print("DEBUG: Calling NewsScheduler.start()")
                await NewsScheduler.start()
                print("DEBUG: NewsScheduler.start() returned")
            except Exception as e:
                print(f"DEBUG: Exception in start(): {e}")
                raise
            
            # Verify Redis client is None
            print(f"DEBUG: redis_client is {NewsScheduler.redis_client}")
            assert NewsScheduler.redis_client is None
            
            # Verify scheduler was started
            mock_scheduler_instance.start.assert_called_once()
            
            # Verify lock factory returns MemoryLock
            lock = NewsScheduler._get_lock("test")
            print(f"DEBUG: Lock type is {type(lock)}")
            assert isinstance(lock, MemoryLock)
            
            # Verify MemoryLock works
            assert await lock.acquire() is True
            assert await lock.release() is True
            
            # Cleanup
            await NewsScheduler.stop()

@pytest.mark.asyncio
async def test_scheduler_with_redis():
    """Test that scheduler uses RedisLock when REDIS_URL is present."""
    
    # Mock settings to have REDIS_URL
    with patch.object(settings, 'redis_url', "redis://localhost:6379/0"):
        # Mock aioredis
        with patch('app.services.news_scheduler.aioredis') as mock_aioredis:
            # Create AsyncMock for redis client
            mock_redis_client = MagicMock()
            mock_redis_client.ping = pytest.AsyncMock()
            mock_redis_client.close = pytest.AsyncMock()
            mock_redis_client.set = pytest.AsyncMock(return_value=True)
            mock_redis_client.eval = pytest.AsyncMock(return_value=True)
            
            # Make from_url return the mock client (it's an async function in code? No, usually it's awaitable or returns client)
            # aioredis.from_url is async? In the code: await aioredis.from_url(...)
            mock_aioredis.from_url = pytest.AsyncMock(return_value=mock_redis_client)
            
            # Mock APScheduler
            with patch('app.services.news_scheduler.AsyncIOScheduler') as MockScheduler:
                mock_scheduler_instance = MagicMock()
                MockScheduler.return_value = mock_scheduler_instance
                
                # Start scheduler
                await NewsScheduler.start()
                
                # Verify Redis client was initialized
                assert NewsScheduler.redis_client is not None
                mock_aioredis.from_url.assert_called_once()
                
                # Verify lock factory returns RedisLock
                lock = NewsScheduler._get_lock("test")
                assert isinstance(lock, RedisLock)
                
                # Cleanup
                await NewsScheduler.stop()
