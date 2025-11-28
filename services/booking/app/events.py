from __future__ import annotations

import asyncio
import json
from typing import Any

from aiokafka import AIOKafkaProducer

from .config import settings

_producer: AIOKafkaProducer | None = None
_lock = asyncio.Lock()


async def start_event_bus() -> None:
    if not settings.kafka_enabled:
        return
    global _producer
    if _producer is None:
        producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap)
        await producer.start()
        _producer = producer


async def stop_event_bus() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def publish_booking_event(event: dict[str, Any]) -> None:
    if not settings.kafka_enabled:
        return
    if _producer is None:
        async with _lock:
            if _producer is None:
                await start_event_bus()
    if _producer is None:
        return
    payload = json.dumps(event).encode("utf-8")
    await _producer.send_and_wait(settings.kafka_topic, payload)
