import sqlite3
import multiprocessing
import time
import logging
from typing import Any
from enum import IntEnum

from config import BASE_DIR, DATABASE_FILENAME, DATABASE_QUEUE_MAX_SIZE

logger: logging.Logger = logging.getLogger(__name__)
queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=DATABASE_QUEUE_MAX_SIZE)

EVENT_KEY: str = "data_type"
LOG_EVENT_TYPE: str = "event"
DATA_EVENT_TYPE: str = "data"


def log_event(message: str, level: int) -> None:
    """
    Adds a log event into the queue to be written.

    Arguments:
        message (str): The message to be written to the database, ex: Sensor Failed!
        level (LogSeverity): The severity of the event, advised to use loggings. Levels
    """
    new_entry: dict[str, Any] = {}
    new_entry[EVENT_KEY] = LOG_EVENT_TYPE
    new_entry["timestamp"] = time.time()

    new_entry["data"] = {}

    new_entry["data"]["message"] = message
    new_entry["data"]["level"] = level

    queue.put(new_entry)


def log_sensor_data(read_data: dict[str, int]) -> None:
    """
    Adds a sensor data event into the queue to be written.

    Arguments:
        data (dict[str, int]): The data to be written locally
    """
    new_entry: dict[str, Any] = {}
    new_entry[EVENT_KEY] = DATA_EVENT_TYPE
    new_entry["timestamp"] = time.time()

    new_entry["data"] = read_data

    queue.put(new_entry)


def process_sensor_data(cursor: sqlite3.Cursor, sensor_entry: dict[str, Any]):
    return


def process_log_event(cursor: sqlite3.Cursor, sensor_entry: dict[str, Any]):
    return


def initialize_database() -> None:
    """
    Attempts to initalize the SQLite database, creating necessary tables if they do not exist
    """

    try:
        db: sqlite3.Connection = sqlite3.connect(f"{BASE_DIR}/data/{DATABASE_FILENAME}")
        cursor: sqlite3.Cursor = db.cursor()

        cursor.execute("PRAGMA journal_mode=WAL")
        result = cursor.execute("PRAGMA journal_mode").fetchone()
        if result[0].lower() != "wal":
            raise RuntimeError(f"WAL mode not set, got: {result[0]}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                probe_id TEXT NOT NULL,
                   
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
                timestamp REAL NOT NULL,
                probe_id TEXT NOT NULL,

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


def update_database_loop():
    """
    Running loop for the database writing thread
    """

    db: sqlite3.Connection = sqlite3.connect(f"{BASE_DIR}/data/{DATABASE_FILENAME}")
    cursor: sqlite3.Cursor = db.cursor()

    try:
        while True:
            new_entry: dict[str, Any] = queue.get()
            event_type: str = new_entry[EVENT_KEY]

            if event_type == LOG_EVENT_TYPE:
                process_log_event(cursor, new_entry)
            elif event_type == DATA_EVENT_TYPE:
                process_sensor_data(cursor, new_entry)
            elif event_type == "SHUTDOWN_SIGNAL":
                db.commit()
                break

            db.commit()
    except Exception as e:
        logger.error(f"Error in the database event loop {e}")
    finally:
        db.close()
