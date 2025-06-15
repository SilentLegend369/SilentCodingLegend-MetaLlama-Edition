"""
Rate limiter for API requests
"""
import asyncio
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter to control API request frequency"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_second: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        self.request_times = []
        self.last_request_time = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make a request"""
        async with self._lock:
            current_time = time.time()
            
            # Remove requests older than 1 minute
            self.request_times = [
                req_time for req_time in self.request_times 
                if current_time - req_time < 60
            ]
            
            # Check per-minute limit
            if len(self.request_times) >= self.requests_per_minute:
                wait_time = 60 - (current_time - self.request_times[0])
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # Check per-second limit
            if current_time - self.last_request_time < (1.0 / self.requests_per_second):
                wait_time = (1.0 / self.requests_per_second) - (current_time - self.last_request_time)
                await asyncio.sleep(wait_time)
                current_time = time.time()
            
            # Record the request
            self.request_times.append(current_time)
            self.last_request_time = current_time
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        current_time = time.time()
        recent_requests = [
            req_time for req_time in self.request_times 
            if current_time - req_time < 60
        ]
        
        return {
            "requests_last_minute": len(recent_requests),
            "requests_per_minute_limit": self.requests_per_minute,
            "requests_per_second_limit": self.requests_per_second,
            "time_since_last_request": current_time - self.last_request_time
        }