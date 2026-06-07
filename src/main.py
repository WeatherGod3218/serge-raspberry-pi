import logging
import sys
import threading
import signal

from core import database, sensor_reader, networking
from config import SESSION_ID, SEND_DATA_TO_SERVER
from modules.appcontext import AppContext, ProbeData

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger: logging.Logger = logging.getLogger(__name__)
running_context: AppContext | None


def shutdown_handler(signum, frame):
    global running_context

    if running_context is None:
        return

    running_context.thread_shutdown.set()

    return


def main():
    global running_context
    logger.info("Creating App Context!")

    running_context = AppContext(
        latest_reading=ProbeData(
            0, 0, None, None, None, None, None, None
        ),  # Should never get read?
        websocket_active=False,
        thread_shutdown=threading.Event(),
        reading_updated=threading.Event(),
    )

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    logger.info("Starting Initalization Sequence!")

    sensor_reader.initalize_sensors()
    database.initialize_database()

    database_thread: threading.Thread = threading.Thread(
        target=database.update_database_loop, args=(running_context,)
    )
    database_thread.start()

    sensor_process: threading.Thread = threading.Thread(
        target=sensor_reader.read_sensor_loop,
        args=(running_context,),
    )
    sensor_process.start()

    logger.info(
        f"Succussfully Initalized All Applications! Current Session ID: {SESSION_ID}"
    )

    websocket_thread: threading.Thread | None = None
    http_thread: threading.Thread | None = None

    if SEND_DATA_TO_SERVER:
        websocket_thread = threading.Thread(
            target=networking.run_websocket_loop, args=(running_context,)
        )
        websocket_thread.start()

        http_thread = threading.Thread(
            target=networking.run_backup_loop, args=(running_context,)
        )
        http_thread.start()
    else:
        logger.warning(
            "Sending data to server was disabled! Skipping over initaliziation!"
        )

    database.log_event(f"STARTED APPLICATION:{SESSION_ID}", logging.INFO)

    running_context.thread_shutdown.wait()

    logger.info("Starting shutdown sequence!")

    database.log_event(f"STOPPED APPLICATION:{SESSION_ID}", logging.INFO)

    logger.info("Shutting down sensors")
    sensor_process.join(timeout=10)

    if sensor_process.is_alive():
        logger.warning("SENSORS DID NOT STOP, KILLING PROCESS!")
    logger.info("Sensor process stopped.")

    logger.info("Stopping database thread!")
    database_thread.join()
    logger.info("Database thread stopped.")

    if websocket_thread:
        logger.info("Stopping websocket thread!")
        websocket_thread.join()
        logger.info("websocket thread stopped.")

    if http_thread:
        logger.info("Stopping http thread!")
        http_thread.join()
        logger.info("Http thread stopped.")

    logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()
