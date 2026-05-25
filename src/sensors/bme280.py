from logging import getLogger, Logger

import board
import busio
from adafruit_bme280 import basic as BME280

from config import SEA_LEVEL_PRESSURE

logger: Logger = getLogger(__name__)

I2C: busio.I2C
sensor: BME280.Adafruit_BME280_I2C


current_pressure: int = 50

# def get_temp() -> float:
#     return "%0.1f" % sensor.temperature

# def get_humidity() -> float:
#     return "%0.1f" % sensor.humidity

# def get_pressure() -> float:
#     return "%0.1f" % sensor.pressure


def get_pressure_test() -> str:
    return "50"

def get_humidity_test() -> str:
    return "69 69 69" 

def get_read_functions():
    return [get_pressure_test, get_humidity_test]


def update():
    raise Exception("MEOW!")

def init_sensor() -> bool:
    """
    Attempts to initalize the BME280 sensor.

    Returns:
        bool: If the probe was able to successfully boot or not
    """
    # global I2C, SENSOR

    # logger.info("Attempting to Initialize the BME280")
    # I2C = busio.I2C(board.SCL, board.SDA)
    # sensor = BME280.Adafruit_BME280_I2C(I2C)

    # sensor.sea_level_pressure = SEA_LEVEL_PRESSURE
    # logger.info("BME280 Initialized!")
    return True

print("BME280 Initialized!")
