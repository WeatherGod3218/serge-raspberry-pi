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

    while not ctx.thread_shutdown.is_set():
        try:
            rows: list[Any] = database.fetch_unsent_rows(cursor)
            logger.info("rows")

            rows_as_json: list[dict[Any, Any]] = [dict(row) for row in rows]

            if not rows_as_json:
                logger.info("No rows to send, skipping")
                continue

            logger.info(f"Sending {len(rows_as_json)} rows")

            async with httpx.AsyncClient(
                headers=headers, timeout=httpx.Timeout(10.0)
            ) as client:
                logger.info("OPENED")
                server_response: httpx.Response = await client.post(
                    HTTP_URL, json={"data": rows_as_json}
                )
                logger.info(f"server response: {server_response.status_code}")

                server_response.raise_for_status()
                logger.info("ack")
                acknowledgement: dict[str, list[dict[str, str | int]]] = (
                    server_response.json()
                )
                logger.info(acknowledgement)
                database.update_sent_rows(cursor, acknowledgement["updated"])
                db.commit()
        except Exception as e:
            logger.exception("FAILED TO BACKUP")
            database.log_event(f"FAILED TO BACKUP! {e}", logging.WARNING)
        finally:
            await asyncio.sleep(DATABASE_BACKUP_DEBOUNCE)


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
