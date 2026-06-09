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

# def get_temp() -> float:
#     return "%0.1f" % sensor.temperature

# def get_humidity() -> float:
#     return "%0.1f" % sensor.humidity

# def get_pressure() -> float:
#     return "%0.1f" % sensor.pressure


def get_pressure_test() -> dict[str, float]:
    """
    Temp function that returns a random pressure amount

    ...Seems like you couldn't handle the... PRESSUREEEEEEEEEEEEE!!!!!!!!!!!!

    Returns:
        dict[str, int]: The pressure recorded with the key "pressure"
    """
    return {"pressure": current_pressure}


def get_humidity_test() -> dict[str, float]:
    """
    Temp function that returns a random humidity amount

    Returns:
        dict[str, int]: The humidty recorded with the key "humidity"
    """
    return {"humidity": current_humidity}


def get_temperature_test() -> dict[str, float]:
    """
    Temp function that returns the temperature

    Returns:
        dict[str, int]: The temperature recorded with the key "temperature"
    """
    global current_temperature

    return {"temperature": current_temperature}


def get_read_functions():
    """
    Returns the list of functions to be processed
    """
    return [get_pressure_test, get_humidity_test, get_temperature_test]


def update() -> None:
    """
    Attempts to update the BME280 sensors' pressure and humidity.

    """
    global sensor, current_humidity, current_pressure, current_temperature

    logger.info(f"Current Sensor: {sensor}")
    current_humidity = sensor.humidity
    current_pressure = sensor.pressure
    current_temperature = sensor.temperature


def init_sensor() -> bool:
    """
    Attempts to initalize the BME280 sensor.

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
