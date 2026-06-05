import sqlite3
import time
import logging
import os
import multiprocessing
import threading
import queue

from dataclasses import dataclass
from config import BASE_DIR, DATABASE_FILENAME, DATABASE_QUEUE_MAX_SIZE, SESSION_ID
from modules.appcontext import AppContext

logger: logging.Logger = logging.getLogger(__name__)
database_queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=DATABASE_QUEUE_MAX_SIZE)

@dataclass(slots=True)
class ProbeEvent:
    timestamp: float
    message: str
    severity: int


@dataclass(slots=True)
class ProbeData:
    timestamp: float

    humidity: float | None
    pressure: float | None
    voc: float | None
    wind_speed: float | None
    co2: float | None
    precipitation: float | None


def log_event(message: str, level: int) -> None:
    """
    Adds a log event into the queue to be written.

    Arguments:
        message (str): The message to be written to the database, ex: Sensor Failed!
        level (LogSeverity): The severity of the event, advised to use loggings. Levels
    """

    new_entry: ProbeEvent = ProbeEvent(
        timestamp=round(time.time(), 2), message=message, severity=level
    )

    database_queue.put(new_entry)


def log_sensor_data(
    humidity: float | None,
    pressure: float | None,
    voc: float | None,
    wind_speed: float | None,
    co2: float | None,
    precipitation: float | None,
) -> None:
    """
    Adds a sensor data event into the queue to be written.

    Arguments:
        data (dict[str, int]): The data to be written locally
    """

    new_entry: ProbeData = ProbeData(
        timestamp=round(time.time(), 2),
        humidity=humidity,
        pressure=pressure,
        voc=voc,
        wind_speed=wind_speed,
        co2=co2,
        precipitation=precipitation,
    )

    database_queue.put(new_entry)


def process_sensor_data(cursor: sqlite3.Cursor, d: ProbeData) -> None:
    """
    Parses data from the sensor to be written to the porbe_data database.

    Arguments:
        cursor (sqlite3.Cursor): The SQLite cursor to use
        d (ProbeData): The data to be written to the database
    """
    cursor.execute(
        """
    INSERT INTO data (session_id, timestamp, humidity, pressure, voc, wind_speed, co2, precipitation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            SESSION_ID,
            d.timestamp,
            d.humidity,
            d.pressure,
            d.voc,
            d.wind_speed,
            d.co2,
            d.precipitation,
        ),
    )


def process_log_event(cursor: sqlite3.Cursor, d: ProbeEvent) -> None:
    """
    Parses data from the sensor to be written to the events database.

    Arguments:
        cursor (sqlite3.Cursor): The SQLite cursor to use
        d (ProbeEvent): The data to be written to the database
    """
    cursor.execute(
        """
    INSERT INTO events (session_id, timestamp, message, severity)
    VALUES (?, ?, ?, ?)
    """,
        (SESSION_ID, d.timestamp, d.message, d.severity),
    )


def initialize_database() -> None:
    """
    Attempts to initalize the SQLite database, creating necessary tables if they do not exist
    """

    logger.info("Attempting to Load Database!")

    try:

        data_dir = f"{BASE_DIR}/data"
        os.makedirs(data_dir, exist_ok=True)

        db: sqlite3.Connection = sqlite3.connect(f"{BASE_DIR}/data/{DATABASE_FILENAME}",timeout=30.0)
        cursor: sqlite3.Cursor = db.cursor()

        cursor.execute("PRAGMA journal_mode=DELETE")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,                
                
                session_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                   
                temperature REAL,
                humidity REAL,
                pressure REAL,
                voc REAL,
                wind_speed REAL,
                co2 REAL,
                precipitation REAL,
                   
                sent INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,                
                session_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                       
                message TEXT,
                severity TEXT,
                   
                sent INTEGER DEFAULT 0
            )
        """)

        db.commit()
        db.close()
    except sqlite3.OperationalError as e:
        logger.critical("DB init failed (operational): %s", e)
        raise
    except sqlite3.DatabaseError as e:
        logger.critical("DB init failed (corrupt or invalid): %s", e)
        raise
    except RuntimeError as e:
        logger.critical("DB init failed: %s", e)
        raise

    logger.info("Successfully loaded the database!")


def update_database_loop(ctx : AppContext):
    """
    Running loop for the database writing thread
    """
    
    loop_database: sqlite3.Connection = sqlite3.connect(f"{BASE_DIR}/data/{DATABASE_FILENAME}")
    cursor: sqlite3.Cursor = loop_database.cursor()

    try:
        while True:            
            try:
                new_entry: ProbeData | ProbeEvent = database_queue.get(timeout=1)
            except queue.Empty:
                if ctx.thread_shutdown.is_set():
                    logger.info("Shutdown detected and queue empty, exiting.")
                    break
                continue

            try:
                if isinstance(new_entry, ProbeEvent):
                    process_log_event(cursor, new_entry)
                elif isinstance(new_entry, ProbeData):
                    process_sensor_data(cursor, new_entry)
                else:
                    logger.warning(f"Unknown entry in the queue! {new_entry}")
            except Exception as e:
                logger.exception(f"Failed to process entry, reverting! {new_entry} with error {e}")
                loop_database.rollback()
            else:
                loop_database.commit()
    finally:
        loop_database.close()

def trigger_shutdown():
    """
    Triggers the shutdown flag for the database to save data and exit
    """
    global shutting_down
    shutting_down = True