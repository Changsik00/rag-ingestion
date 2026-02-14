import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    """
    Internal Asynchronous Event Bus for decoupling system components.
    Implemented as a singleton to ensure a single event flow within the process.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = defaultdict(list)
        return cls._instance

    def subscribe(self, event_type: str, handler: Callable[[Any], Coroutine[Any, Any, None]]):
        """Subscribe a coroutine handler to an event type."""
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(f"Subscribed handler {handler.__name__} to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable[[Any], Coroutine[Any, Any, None]]):
        """Unsubscribe a handler from an event type."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Unsubscribed handler {handler.__name__} from {event_type}")

    def clear(self):
        """Clear all registered handlers. Useful for testing."""
        self._handlers.clear()
        logger.debug("EventBus cleared")

    async def publish(self, event_type: str, data: Any):
        """
        Publish an event to all subscribers.
        Handlers are executed concurrently.
        """
        handlers = self._handlers.get(event_type, [])
        if not handlers:
            logger.debug(f"No handlers for event {event_type}")
            return

        logger.debug(f"Publishing {event_type} to {len(handlers)} handlers")

        # Execute all handlers concurrently as individual tasks
        tasks = [asyncio.create_task(handler(data)) for handler in handlers]
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    handler_name = handlers[i].__name__ if i < len(handlers) else "unknown"
                    logger.error(f"Error in handler '{handler_name}' for {event_type}: {res}", exc_info=res)


# Global singleton instance
bus = EventBus()
