import types
import time
import logging

from sensors import bme280
from config import SENSOR_FAIL_SHUTDOWN_LIMIT, SENSOR_READING_DEBOUNCE_TIME
from modules import database
from modules.appcontext import AppContext, ProbeData

LOADED_SENSORS: list[types.ModuleType] = [bme280]

sensor_map: dict[types.ModuleType, list[types.FunctionType]] = {}
failed_sensors: dict[types.ModuleType, int] = {}

logger: logging.Logger = logging.getLogger(__name__)
current_sequence_number: int = 1


def process_failed_sensor(sensor: types.ModuleType, e: Exception) -> None:
    """
    Processes a failed sensor, removing it from running sensors if above the configurated SENSOR_FAIL_SHUTDOWN_LIMIT

    Arguments:
        sensor (types.ModuleType): The sensor that failed
    """
    global sensor_map, failed_sensors, logger

    if sensor in failed_sensors:
        failed_sensors[sensor] += 1
        if failed_sensors[sensor] > SENSOR_FAIL_SHUTDOWN_LIMIT:
            sensor_map.pop(sensor, None)
            failed_sensors.pop(sensor, None)
            logger.warning(
                f"SENSOR {sensor.__name__} HAS FAILED MORE THAN {SENSOR_FAIL_SHUTDOWN_LIMIT} TIMES, REMOVING IT FROM PROCESSING!"
            )
            database.log_event(
                f"SENSOR {sensor.__name__} HAS FAILED MORE THAN {SENSOR_FAIL_SHUTDOWN_LIMIT} TIMES, REMOVING IT FROM PROCESSING!",
                logging.WARNING,
            )
            return
    else:
        failed_sensors[sensor] = 1

    logger.warning(
        f"SENSOR {sensor.__name__} HAS FAILED {failed_sensors[sensor]} TIMES! SENSOR WILL CONTINUE TO BE PROCESSED"
    )

    database.log_event(
        f"SENSOR {sensor.__name__} HAS FAILED {failed_sensors[sensor]} TIMES! SENSOR WILL CONTINUE TO BE PROCESSED: {e}",
        logging.WARNING,
    )


def update_sensor(sensor: types.ModuleType) -> Exception | None:
    """
    Processes a sensor, safely updating attributes to be read

    Arguments:
        sensor (types.ModuleType): The sensor to be processed
    """
    global sensor_map, failed_sensors, logger

    try:
        sensor.update()
        return None
    except Exception as e:
        logger.warning(f"SENSOR {sensor.__name__} FAILED WITH ERROR: {e}")
        process_failed_sensor(sensor, e)
        return e


def initalize_sensors() -> None:
    """
    Loads all sensors from the LOADED SENSORS, ensuring that both an "update" and "get_read_functions" exists
    """
    global LOADED_SENSORS, sensor_map

    logger.info("Attempting to Load Sensors!")

    for sensor in LOADED_SENSORS:
        if not hasattr(sensor, "init_sensor"):
            logger.warning(
                f"SENSOR {sensor.__name__} DOES NOT HAVE AN update FUNCTION! PASSING SENSOR FROM LOADING"
            )
            continue

        if not hasattr(sensor, "update"):
            logger.warning(
                f"SENSOR {sensor.__name__} DOES NOT HAVE AN update FUNCTION! PASSING SENSOR FROM LOADING"
            )
            continue

        if not hasattr(sensor, "get_read_functions"):
            logger.warning(
                f"SENSOR {sensor.__name__} DOES NOT HAVE get_read_functions FUNCTION! PASSING SENSOR FROM LOADING"
            )
            continue

        try:
            sensor_map[sensor] = sensor.init_sensor()
        except Exception:
            logger.exception(f"SENSOR {sensor.__name__} FAILED TO INITALIZE!")
            continue

        sensor_map[sensor] = sensor.get_read_functions()

        if not isinstance(sensor_map[sensor], list):
            logger.warning(
                f"SENSOR {sensor.__name__} DID NOT RETURN A LIST OF FUNCTIONS FOR get_read_functions"
            )
            sensor_map.pop(sensor, None)

        logger.info(f"Successfully loaded the sensor {sensor.__name__}")

    logger.info(f"Sensors Loaded Successfully! {sensor_map}")


def read_sensor_loop(ctx: AppContext):
    """
    Running loop for the sensor reading thread
    """
    global sensor_map, current_sequence_number

    while not ctx.thread_shutdown.is_set():
        newest_map: dict[str, float] = {}

        for sensor, func_list in list(sensor_map.items()):
            error_updating_sensor: Exception | None = update_sensor(sensor)

            if error_updating_sensor:
                logger.warning(f"{error_updating_sensor}")
                continue

            for function in func_list:
                newest_map.update(function())

        new_data: ProbeData = ProbeData(
            sequence=current_sequence_number,
            temperature=newest_map.get("temperature"),
            humidity=newest_map.get("humidity"),
            pressure=newest_map.get("pressure"),
            voc=newest_map.get("voc"),
            wind_speed=newest_map.get("wind_speed"),
            co2=newest_map.get("co2"),
            precipitation=newest_map.get("precipitation"),
        )

        ctx.latest_reading = new_data

        ctx.event_loop.call_soon_threadsafe(ctx.server_update.set)
        ctx.event_loop.call_soon_threadsafe(ctx.laptop_update.set)

        database.log_sensor_data(new_data)
        current_sequence_number += 1

        time.sleep(SENSOR_READING_DEBOUNCE_TIME)
