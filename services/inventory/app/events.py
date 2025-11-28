from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress

from aiokafka import AIOKafkaConsumer
from sqlmodel import Session

from .config import settings
from .database import engine
from .models import ViewingSession

logger = logging.getLogger(__name__)

_consumer: AIOKafkaConsumer | None = None
_task: asyncio.Task[None] | None = None


async def start_event_consumer() -> None:
    if not settings.kafka_enabled:
        return
    global _consumer, _task
    if _consumer is not None:
        return
    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap,
        group_id="inventory-service",
        enable_auto_commit=True,
    )
    await consumer.start()
    _consumer = consumer

    async def _consume() -> None:
        try:
            assert _consumer is not None
            async for message in _consumer:
                try:
                    payload = json.loads(message.value)
                except json.JSONDecodeError:
                    logger.warning("Invalid booking event payload")
                    continue
                await handle_booking_event(payload)
        except asyncio.CancelledError:
            pass

    _task = asyncio.create_task(_consume())


async def stop_event_consumer() -> None:
    global _consumer, _task
    if _task is not None:
        _task.cancel()
        with suppress(asyncio.CancelledError):
            await _task
        _task = None
    if _consumer is not None:
        await _consumer.stop()
        _consumer = None


async def handle_booking_event(payload: dict) -> None:
    event_id = payload.get("event_id")
    seats = int(payload.get("seats", 1))
    if not event_id:
        return
    with Session(engine) as session:
        event = session.get(ViewingSession, event_id)
        if event is None:
            return
        event.slots_available = max(event.slots_available - seats, 0)
        session.add(event)
        session.commit()
