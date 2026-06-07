import threading
from dataclasses import dataclass


@dataclass(slots=True)
class AppContext:
    latest_reading: ProbeData
    websocket_active: bool
    thread_shutdown: threading.Event
    reading_updated: threading.Event


@dataclass(slots=True)
class ProbeEvent:
    timestamp: float
    message: str
    severity: int


@dataclass(slots=True)
class ProbeData:
    timestamp: float
    sequence: int

    humidity: float | None
    pressure: float | None
    voc: float | None
    wind_speed: float | None
    co2: float | None
    precipitation: float | None
