# from sgp30 import SGP30
import time
import datetime
import sys
import json

# sgp30 = SGP30()

# Initilizing Sensor
print("Initialzing SGP30 Sensor...(Estimated 15-20 Seconds)")
start_time = time.time()

# sgp30.start_measurement()

# ⏱️ Start timer

# def get_co2_air_quality():
#     return str(sgp30.get_air_quality().equivalent_co2)

# def get_total_voc():
#     return str(sgp30.get_air_quality().total_voc)


def init_sensor() -> bool:
    """
    Attempts to initalize the SGP30 sensor.

    Returns:
        bool: If the sensor was able to successfully boot or not
    """
    start_time = time.time()

    # global I2C, SENSOR

    # logger.info("Attempting to Initialize the BME280")
    # I2C = busio.I2C(board.SCL, board.SDA)
    # sensor = BME280.Adafruit_BME280_I2C(I2C)

    # sensor.sea_level_pressure = SEA_LEVEL_PRESSURE
    # logger.info("BME280 Initialized!")
    return True


elapsed_time = round(time.time() - start_time, 2)
print("SGP30 Sensor Initialized in ", elapsed_time, " Seconds!")
