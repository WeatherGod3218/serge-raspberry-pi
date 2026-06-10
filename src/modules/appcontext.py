import threading
from dataclasses import dataclass, field
import uuid_utils as uuid
import time
import asyncio


@dataclass(slots=True)
class ProbeEvent:
    """
    Class for "Events" that occur during operation. Thing like Sensors Disconnecting, Application Starting, etc

    Attributes:
        message (str): The message of the event
        severity (int): The level of severity of the incident (similar to loggers logger.WARNING Enum style)

        record_id (str): An automatically generated UUID7 for logging purposes
        timestamp (float): An automatically generated timestamp using the Unix epoch
    """

    message: str
    severity: int

    record_id: str = field(default_factory=lambda: str(uuid.uuid7()))
    timestamp: float = field(default_factory=time.time)


@dataclass(slots=True)
class ProbeData:
    """
    Class for data readings taken by the probe during operation.

    Attributes:
        sequence (int): The "sequence" of the reading. An auto-incrementing number from the start of the run for ordering purposes

        temperature (float | None): The temperature reading, in Celcius
        humidity (float | None): The humidity reading, in Relative Humidity (percentage of vapor -> air)
        pressure (float | None): The pressure reading, in Barometric Pressure
        pressure (float | None): The pressure reading, in Barometric Pressure
        voc (float | None): The tVOC reading, in Parts Per Billion
        wind_speed (float | None): The Wind Speed, in GOD knows what!
        co2 (float | None): The eCO2, in Parts Per Million
        precipitation (float | None): The Precipitation amount, in GOD knows what!

        record_id (str): An automatically generated UUID7 for logging purposes
        timestamp (float): An automatically generated timestamp using the Unix epoch
    """

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
    """
    Class for the applications running context

    Attributes:
        event_loop (asyncio.AbstractEventLoop): The running asyncio loop to be used throughout the application

        server_connected (bool): Is the backup server connected?
        server_update: (asyncio.Event): Event that fires whenever a reading is taken for the server to update

        laptop_connected (bool): Is the local laptop connected?
        server_update: (asyncio.Event): Event that fires whenever a reading is taken for the laptop to update

        latest_reading (ProbeData): The most recent reading from the probe, None if none has been taken yet
        thread_shutdown (threading.Event): The multi-thread event that fires to start shutting down the application gracefully
    """

    event_loop: asyncio.AbstractEventLoop

    server_connected: bool = False
    server_update: asyncio.Event = asyncio.Event()

    laptop_connected: bool = False
    laptop_update: asyncio.Event = asyncio.Event()

    latest_reading: ProbeData | None = None
    thread_shutdown: threading.Event = threading.Event()
