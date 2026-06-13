from logging import getLogger, Logger

import adafruit_sgp30
import board
import busio
import time
from modules.appcontext import AppContext


logger: Logger = getLogger(__name__)

sensor: adafruit_sgp30.Adafruit_SGP30 | None = None
I2C: busio.I2C | None = None

current_eco2: float = 0
current_tvoc: float = 0


def get_co2() -> dict[str, float]:
    """
    Returns the latest eco2 reading from the sensor safely

    Returns:
        dict[str, int]: The eco2 recorded with the key "co2"
    """
    global current_eco2

    return {"co2": current_eco2}


def get_voc() -> dict[str, float]:
    """
    Returns the latest tvoc reading from the sensor safely

    Returns:
        dict[str, int]: The tvoc recorded with the key "voc"
    """
    global current_tvoc

    return {"voc": current_tvoc}


def get_read_functions():
    """
    Returns the list of functions to be processed
    """
    return [get_co2, get_voc]


def update(ctx: AppContext) -> None:
    """
    Attempts to update the SGP30 sensors' pressure and humidity. using the BME280s recent readings to calibrate

    Arguments:
        ctx (AppContext): The running app context
    """
    global sensor, current_tvoc, current_eco2

    if not sensor:
        raise RuntimeError("SGP30 was not initalized!")

    if (
        ctx.latest_reading
        and ctx.latest_reading.temperature
        and ctx.latest_reading.humidity
    ):
        sensor.set_iaq_relative_humidity(
            ctx.latest_reading.temperature, ctx.latest_reading.humidity
        )

    current_eco2 = sensor.eCO2
    current_tvoc = sensor.TVOC


def init_sensor(_) -> bool:
    """
    Attempts to initalize the SGP30 sensor.

    Arguments:
        ctx (AppContext): The running app context

    Returns:
        bool: If the sensor was able to successfully boot or not
    """
    global I2C, sensor

    I2C = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_sgp30.Adafruit_SGP30(I2C)
    sensor.iaq_init()
    time.sleep(15)
    # logger.info("Attempting to Initialize the BME280")
    # I2C = busio.I2C(board.SCL, board.SDA)
    # sensor = BME280.Adafruit_BME280_I2C(I2C)

    # sensor.sea_level_pressure = SEA_LEVEL_PRESSURE
    # logger.info("BME280 Initialized!")
    return True
