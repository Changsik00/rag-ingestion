import asyncio

import pytest

from app.core.events import EventBus


@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = EventBus()
    received_data = []

    async def handler(data: str):
        received_data.append(data)

    bus.subscribe("test_event", handler)
    await bus.publish("test_event", "hello")

    # Give it a tiny bit of time to process if it's queued,
    # though with a direct call it might be immediate.
    await asyncio.sleep(0.01)

    assert "hello" in received_data

@pytest.mark.asyncio
async def test_event_bus_multiple_handlers():
    bus = EventBus()
    count = 0

    async def handler1(data: int):
        nonlocal count
        count += data

    async def handler2(data: int):
        nonlocal count
        count += data * 2

    bus.subscribe("add", handler1)
    bus.subscribe("add", handler2)

    await bus.publish("add", 10)
    await asyncio.sleep(0.01)

    assert count == 30  # 10 + 20

@pytest.mark.asyncio
async def test_event_bus_unsubscribe():
    bus = EventBus()
    received = []

    async def handler(data):
        received.append(data)

    bus.subscribe("event", handler)
    await bus.publish("event", "first")
    await asyncio.sleep(0.01)

    bus.unsubscribe("event", handler)
    await bus.publish("event", "second")
    await asyncio.sleep(0.01)

    assert received == ["first"]
