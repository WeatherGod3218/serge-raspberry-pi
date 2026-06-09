import threading
from dataclasses import dataclass, field
import uuid_utils as uuid
import time
import asyncio


@dataclass(slots=True)
class ProbeEvent:
    message: str
    severity: int

    record_id: str = field(default_factory=lambda: str(uuid.uuid7()))
    timestamp: float = field(default_factory=time.time)


@dataclass(slots=True)
class ProbeData:
    sequence: int
    temperature: float | None
    humidity: float | None
    pressure: float | None
    voc: float | None
    wind_speed: float | None
    co2: float | None
    precipitation: float | None

    record_id: str = field(default_factory=lambda: str(uuid.uuid7()))
    timestamp: float = field(default_factory=time.time)


@dataclass(slots=True)
class AppContext:
    event_loop: asyncio.AbstractEventLoop

    server_connected: bool = False
    server_update: asyncio.Event = asyncio.Event()

    laptop_connected: bool = False
    laptop_update: asyncio.Event = asyncio.Event()

    latest_reading: ProbeData | None = None
    thread_shutdown: threading.Event = threading.Event()
