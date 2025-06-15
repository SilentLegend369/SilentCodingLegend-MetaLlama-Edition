"""
Async utilities for handling coroutines safely in different contexts
"""
import asyncio
import threading
from typing import Any, Coroutine, Optional
import logging

logger = logging.getLogger(__name__)


def run_async_safely(coro: Coroutine) -> Any:
    """
    Run an async coroutine safely, handling event loop issues
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        
        # Check if the loop is running
        if loop.is_running():
            # If the loop is running, we need to run in a thread
            logger.debug("Event loop is running, executing in thread")
            
            result = None
            exception = None
            
            def run_in_thread():
                nonlocal result, exception
                try:
                    # Create a new event loop for this thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            return result
        else:
            # If the loop is not running, we can run directly
            logger.debug("Event loop not running, executing directly")
            return loop.run_until_complete(coro)
            
    except RuntimeError:
        # No event loop exists, create one
        logger.debug("No event loop exists, creating new one")
        return asyncio.run(coro)
    except Exception as e:
        logger.error(f"Error running async coroutine: {e}")
        raise


def create_async_task(coro: Coroutine) -> Optional[asyncio.Task]:
    """
    Create an async task safely
    
    Args:
        coro: The coroutine to create a task for
        
    Returns:
        The created task or None if not possible
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.create_task(coro)
    except RuntimeError:
        pass
    
    logger.warning("Cannot create task - no running event loop")
    return None


async def run_with_timeout(coro: Coroutine, timeout: float = 30.0) -> Any:
    """
    Run a coroutine with a timeout
    
    Args:
        coro: The coroutine to run
        timeout: Timeout in seconds
        
    Returns:
        The result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If the coroutine times out
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Coroutine timed out after {timeout} seconds")
        raise