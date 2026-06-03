import types
import time

from logging import getLogger, Logger

from sensors import bme280
from config import SENSOR_FAIL_SHUTDOWN_LIMIT

LOADED_SENSORS: list[types.ModuleType] = [bme280]

sensor_map: dict[types.ModuleType, list[types.FunctionType]] = {}
failed_sensors: dict[types.ModuleType, int] = {}

logger: Logger = getLogger(__name__)


def process_failed_sensor(sensor: types.ModuleType) -> None:
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
            return
    else:
        failed_sensors[sensor] = 1

    logger.warning(
        f"SENSOR {sensor.__name__} HAS FAILED {failed_sensors[sensor]} TIMES! SENSOR WILL CONTINUE TO BE PROCESSED"
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
        process_failed_sensor(sensor)
        return e


def load_sensors():
    """
    Loads all sensors from the LOADED SENSORS, ensuring that both an "update" and "get_read_functions" exists
    """
    global LOADED_SENSORS, sensor_map

    for sensor in LOADED_SENSORS:
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

        sensor_map[sensor] = sensor.get_read_functions()

        if not isinstance(sensor_map[sensor], list):
            logger.warning(
                f"SENSOR {sensor.__name__} DID NOT RETURN A LIST OF FUNCTIONS FOR get_read_functions"
            )
            sensor_map.pop(sensor, None)

        logger.info(f"Succesfully loaded the sensor {sensor.__name__}")


def read_sensor_loop():
    """
    Running loop for the sensor reading thread
    """
    global sensor_map

    while True:
        for sensor, _ in list(sensor_map.items()):
            error_updating_sensor: Exception | None = update_sensor(sensor)

            if error_updating_sensor:
                logger.warning(f"{error_updating_sensor}")
                continue

            for function in sensor_map[sensor]:
                result: str = function()
                formatted_string: str = f"({sensor.__name__}): {result}"

                logger.info(formatted_string)

        time.sleep(1)
