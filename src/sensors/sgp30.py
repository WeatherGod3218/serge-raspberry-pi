from sgp30 import SGP30
import time
import datetime
import sys
import json

sgp30 = SGP30()

#Initilizing Sensor
print("Initialzing SGP30 Sensor...(Estimated 15-20 Seconds)")
start_time = time.time()

sgp30.start_measurement()

# ⏱️ Start timer

def get_co2_air_quality():
    return str(sgp30.get_air_quality().equivalent_co2)

def get_total_voc():
    return str(sgp30.get_air_quality().total_voc)

elapsed_time = round(time.time() - start_time, 2)
print("SGP30 Sensor Initialized in ", elapsed_time, " Seconds!")
