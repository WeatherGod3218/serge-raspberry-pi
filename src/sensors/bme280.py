from logging import getLogger, Logger
import random

# import board
import busio
from adafruit_bme280 import basic as BME280


logger: Logger = getLogger(__name__)

I2C: busio.I2C
sensor: BME280.Adafruit_BME280_I2C


current_pressure: float = 50
current_humidity: float = 60
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


def get_read_functions():
    """
    Returns the list of functions to be processed
    """
    return [get_pressure_test, get_humidity_test]


def update() -> None:
    """
    Attempts to update the BME280 sensors' pressure and humidity.

    """
    global current_humidity, current_pressure

    current_humidity = random.randint(20, 60)
    current_pressure = random.randint(20, 60)


def init_sensor() -> bool:
    """
    Attempts to initalize the BME280 sensor.

    Returns:
        bool: If the sensor was able to successfully boot or not
    """
    # global I2C, SENSOR

    # logger.info("Attempting to Initialize the BME280")
    # I2C = busio.I2C(board.SCL, board.SDA)
    # sensor = BME280.Adafruit_BME280_I2C(I2C)

    # sensor.sea_level_pressure = SEA_LEVEL_PRESSURE
    # logger.info("BME280 Initialized!")
    return True
