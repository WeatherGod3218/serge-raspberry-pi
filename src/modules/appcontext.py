import threading
from dataclasses import dataclass, field
import uuid_utils as uuid
import time


@dataclass(slots=True)
class AppContext:
    latest_reading: ProbeData
    websocket_active: bool
    thread_shutdown: threading.Event
    reading_updated: threading.Event


@dataclass(slots=True)
class ProbeEvent:
    message: str
    severity: int

    record_id: str = field(default_factory=lambda: str(uuid.uuid7()))
    timestamp: float = field(default_factory=time.time)


@dataclass(slots=True)
class ProbeData:
    sequence: int
    humidity: float | None
    pressure: float | None
    voc: float | None
    wind_speed: float | None
    co2: float | None
    precipitation: float | None

    record_id: str = field(default_factory=lambda: str(uuid.uuid7()))
    timestamp: float = field(default_factory=time.time)
