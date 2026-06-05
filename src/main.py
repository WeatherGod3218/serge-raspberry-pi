import logging
import sys
import threading
import signal

from core import database, sensor_reader
from config import SESSION_ID, SEND_DATA_TO_SERVER
from modules.appcontext import AppContext

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
        thread_shutdown=threading.Event(),
    )

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    logger.info("Starting Initalization Sequence!")

    sensor_reader.initalize_sensors()
    database.initialize_database()

    if SEND_DATA_TO_SERVER:
        pass
    else:
        logger.warning(
            f"Sending data to server was disabled! Skipping over initaliziation!"
        )


    database_thread = threading.Thread(
        target=database.update_database_loop,
        args=(running_context,)
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
    networking_thread = threading.Thread()

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

    logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
