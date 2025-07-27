from functools import wraps
import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

def cache_response(cache_key_template: str, expiration: int = 3600):
    """
    Decorator to cache API responses using Redis
    
    Args:
        cache_key_template: Template for cache key (can use {param_name} placeholders)
        expiration: Cache expiration time in seconds
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            from app.services.transfer_service import TransferPlanService

            service = TransferPlanService()
            redis_client = service.redis_client

            cache_key = cache_key_template.format(**kwargs)
            
            # Check cache first
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for {cache_key}")
                    return json.loads(cached_result)

            except Exception as e:
                logger.warning(f"Cache read error for {cache_key}: {e}")
            
            # Cache miss - execute function
            logger.info(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)

            try:
                redis_client.set(cache_key, json.dumps(result), ex=expiration)
                logger.info(f"Cached result for {cache_key} (expires in {expiration}s)")
            except Exception as e:
                logger.warning(f"Cache write error for {cache_key}: {e}")
            
            return result
        
        return wrapper
    
    return decorator