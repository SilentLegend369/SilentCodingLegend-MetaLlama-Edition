"""
Retry handler for API requests with exponential backoff
"""
import asyncio
import random
import logging
from typing import Callable, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class RetryHandler:
    """Handle retries for failed API requests with exponential backoff"""
    
    def __init__(
        self, 
        max_retries: int = 3, 
        base_delay: float = 1.0, 
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the next retry attempt"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter to prevent thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable"""
        if isinstance(error, httpx.HTTPStatusError):
            # Retry on server errors and rate limits
            return error.response.status_code in [429, 500, 502, 503, 504]
        elif isinstance(error, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError)):
            return True
        elif isinstance(error, httpx.RequestError):
            return True
        
        return False
    
    async def execute(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Execute a function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) exceeded for function {func.__name__}")
                    raise e
                
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise e
                
                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        raise last_exception
    
    def get_config(self) -> dict:
        """Get retry handler configuration"""
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "exponential_base": self.exponential_base,
            "jitter": self.jitter
        }