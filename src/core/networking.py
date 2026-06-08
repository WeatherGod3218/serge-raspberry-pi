import asyncio
import logging
import httpx
import websockets
import json
import sqlite3

from typing import Any
from core import database
from config import (
    SERVER_API_KEY,
    HTTP_URL,
    WS_URL,
    DATABASE_BACKUP_DEBOUNCE,
    WEBSOCKET_RECONNECT_DEBOUNCE,
    BASE_DIR,
    DATABASE_FILENAME,
)
from modules.appcontext import AppContext, ProbeData

logger: logging.Logger = logging.getLogger(__name__)


async def backup_data(ctx: AppContext):
    """
    Attempts to connect to the server for data export
    """
    if SERVER_API_KEY in (None, ""):
        return

    if HTTP_URL in (None, ""):
        return

    headers: dict[str, str] = {
        "Authorization": f"Bearer {SERVER_API_KEY}",
        "Content-Type": "application/json",
    }

    db: sqlite3.Connection = sqlite3.connect(
        f"{BASE_DIR}/data/{DATABASE_FILENAME}", timeout=30.0
    )
    db.row_factory = sqlite3.Row
    cursor: sqlite3.Cursor = db.cursor()

    client = httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(10.0))

    try:
        while not ctx.thread_shutdown.is_set():
            event_rows: list[Any] = database.fetch_unsent_events(cursor)
            data_rows: list[Any] = database.fetch_unsent_data(cursor)

            if (not event_rows) and (not data_rows):
                await asyncio.sleep(DATABASE_BACKUP_DEBOUNCE)
                continue

            event_rows_json = [dict(r) for r in event_rows]
            data_rows_json = [dict(r) for r in data_rows]

            try:
                resp = await client.post(
                    HTTP_URL, json={"events": event_rows_json, "data": data_rows_json}
                )
                resp.raise_for_status()

                ack = resp.json()
                database.update_sent_data(cursor, [row["id"] for row in ack["data"]])
                database.update_sent_events(
                    cursor, [row["id"] for row in ack["events"]]
                )
                db.commit()

            except Exception as e:
                logger.exception("FAILED TO BACKUP")
                database.log_event(f"FAILED TO BACKUP! {e}", logging.WARNING)
                db.rollback()
            await asyncio.sleep(DATABASE_BACKUP_DEBOUNCE)

    finally:
        await client.aclose()


async def initialize_server_connection(ctx: AppContext):
    """
    Initialize the connection the websocket
    """

    if not SERVER_API_KEY:
        return

    if not WS_URL:
        return

    headers: dict[str, str] = {
        "Authorization": f"Bearer {SERVER_API_KEY}",
    }

    while not ctx.thread_shutdown.is_set():
        try:
            async with websockets.connect(
                WS_URL, ping_interval=20, ping_timeout=10, additional_headers=headers
            ) as client:
                ctx.websocket_active = True
                database.log_event("WEBSOCKET CONNECTED!", logging.INFO)

                while not ctx.thread_shutdown.is_set():
                    ctx.reading_updated.wait()
                    ctx.reading_updated.clear()

                    reading: ProbeData = ctx.latest_reading

                    data: dict[str, float | None] = {
                        "timestamp": reading.timestamp,
                        "co2": reading.co2,
                        "humidity": reading.humidity,
                        "precipitation": reading.precipitation,
                        "pressure": reading.pressure,
                        "voc": reading.voc,
                        "wind_speed": reading.wind_speed,
                    }

                    await client.send(json.dumps(data))
        except Exception as e:
            if ctx.websocket_active:
                logger.warning(f"FAILED TO BACKUP! {e}")
                database.log_event(f"WEBSOCKET DISCONNECTED! {e}", logging.WARNING)
        finally:
            ctx.websocket_active = False

        if ctx.thread_shutdown.is_set():
            break

        await asyncio.sleep(WEBSOCKET_RECONNECT_DEBOUNCE)


def run_backup_loop(ctx: AppContext):
    asyncio.run(backup_data(ctx))


def run_websocket_loop(ctx: AppContext):
    asyncio.run(initialize_server_connection(ctx))
