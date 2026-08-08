import asyncio
import logging
from typing import Callable, Coroutine, Dict, List, Any

logger = logging.getLogger("marine_twin.events")

class EventBus:
    def __init__(self):
        # Map event types to a list of asynchronous callbacks
        self._listeners: Dict[str, List[Callable[[Any], Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, event_type: str, listener: Callable[[Any], Coroutine[Any, Any, None]]):
        """Register an async callback for a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if listener not in self._listeners[event_type]:
            self._listeners[event_type].append(listener)
            logger.info(f"Subscribed callback listener to event: {event_type}")

    def unsubscribe(self, event_type: str, listener: Callable[[Any], Coroutine[Any, Any, None]]):
        """Deregister an async callback."""
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
            logger.info(f"Deregistered callback listener from event: {event_type}")

    async def publish(self, event_type: str, data: Any):
        """Asynchronously broadcast data to all subscribed listeners."""
        if event_type not in self._listeners or not self._listeners[event_type]:
            return
        
        # Dispatch event callbacks concurrently
        tasks = [
            asyncio.create_task(self._safe_execute(listener, event_type, data))
            for listener in self._listeners[event_type]
        ]
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, listener: Callable[[Any], Coroutine[Any, Any, None]], event_type: str, data: Any):
        """Ensure callbacks are executed safely without halting the event bus in case of failures."""
        try:
            await listener(data)
        except Exception as e:
            logger.error(
                f"Exception raised in event handler for topic '{event_type}': {e}",
                exc_info=True,
                extra={"extra_context": {"event": event_type, "payload": str(data)}}
            )

# Shared Event Bus singleton
event_bus = EventBus()
