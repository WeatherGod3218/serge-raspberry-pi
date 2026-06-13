from logging import getLogger, Logger

import board
import busio
from adafruit_bme280 import basic as BME280
from config import SEA_LEVEL_PRESSURE

logger: Logger = getLogger(__name__)

sensor: BME280.Adafruit_BME280_I2C | None = None
I2C: busio.I2C | None = None


current_pressure: float = 0
current_humidity: float = 0
current_temperature: float = 0


def get_pressure() -> dict[str, float]:
    """
    Returns the latest pressure reading from the sensor safely

    ...Seems like you couldn't handle the... PRESSUREEEEEEEEEEEEE!!!!!!!!!!!!

    Returns:
        dict[str, int]: The pressure recorded with the key "pressure"
    """
    return {"pressure": current_pressure}


def get_humidity() -> dict[str, float]:
    """
    Returns the latest humidty reading from the sensor safely

    Returns:
        dict[str, int]: The humidty recorded with the key "humidity"
    """
    return {"humidity": current_humidity}


def get_temperature() -> dict[str, float]:
    """
    Returns the latest temperature reading from the sensor safely

    Returns:
        dict[str, int]: The temperature recorded with the key "temperature"
    """
    global current_temperature

    return {"temperature": current_temperature}


def get_read_functions():
    """
    Returns the list of functions to be processed
    """
    return [get_pressure, get_humidity, get_temperature]


def update(_) -> None:
    """
    Attempts to update the BME280 sensors' pressure and humidity.

    Arguments:
        ctx (AppContext): The running app context
    """
    global sensor, current_humidity, current_pressure, current_temperature

    if not sensor:
        raise RuntimeError("BME280 was not initalized!")

    current_humidity = sensor.humidity
    current_pressure = sensor.pressure
    current_temperature = sensor.temperature


def init_sensor(_) -> bool:
    """
    Attempts to initalize the BME280 sensor.

    Arguments:
        ctx (AppContext): The running app context

    Returns:
        bool: If the sensor was able to successfully boot or not
    """
    global I2C, sensor

    logger.info("Attempting to Initialize the BME280")
    I2C = busio.I2C(board.SCL, board.SDA)
    sensor = BME280.Adafruit_BME280_I2C(I2C)

    sensor.sea_level_pressure = SEA_LEVEL_PRESSURE
    logger.info(f"BME280 Initialized! {sensor}")
    return True
