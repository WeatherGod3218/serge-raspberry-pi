# #make all sensors functions
# #master class should run everything wgen this one runs
# import time
# import datetime
# import json

# import sensors.bme280 as bme280

# foundW1thermSensor = False

# try:
#     import W1Therm_Class as w1therm
#     foundW1thermSensor = True
# except:
#     print("UNABLE TO LOAD W1THERM SENSOR, WILL NOT ATTEMPT TO RECORD DATA")
#     foundW1thermSensor = False

# # Make sure SGP30 is last due to 15 second boot time
# import sensors.sgp30 as sgp30

# INTERVAL_TIME = 2.5  # In seconds, determines how long in between each attempt to read/write data (NOT INCLUDING LENGTH IT TAKES FOR SENSORS)
    
# start_time = time.time() # Start of the running period, used for the File
# errors_on_scan = 0

# def attemptCall(func):
#     try:
#         return func()
#     except:
#         global errors_on_scan
#         print("Error Occured with Function: " + str(func))
#         errors_on_scan += 1
#         return "NULL"



# def main():
    
#     while True:
#         global errors_on_scan,foundW1thermSensor
#         errors_on_scan = 0
#         now = datetime.datetime.now() # Date
#         current_Time = now.time() #Get the time at the Current Read

#         newDictionary = {} # New Dictionary
#         if foundW1thermSensor:
#             newDictionary[str(current_Time)] = {
#             '(SGP30) CO2 Level: ' : attemptCall(sgp30.get_co2_air_quality) + "ppm",
#             '(SGP30) Total VOC: ' : attemptCall(sgp30.get_total_voc) + "ppm",

#             '(BME280) Tempature (Celsius): ' : attemptCall(bme280.get_temp) + "C",
#             '(BME280) Humidity: ' : attemptCall(bme280.get_humidity) + "rh",
#             '(BME280) Pressure: ' : attemptCall(bme280.get_pressure) + "hP",

#             '(W1Therm) Tempature (Celsius): ' : attemptCall(w1therm.get_temp_C) + "C",
#             '(W1Therm) Tempature (Fahrenheit): ' : attemptCall(w1therm.get_temp_F) + "F"
#             } # Get Values from Sensors
#         else:
#             newDictionary[str(current_Time)] = {
#             '(SGP30) CO2 Level: ' : attemptCall(sgp30.get_co2_air_quality) + "ppm",
#             '(SGP30) Total VOC: ' : attemptCall(sgp30.get_total_voc) + "ppm",

#             '(BME280) Tempature (Celsius): ' : attemptCall(bme280.get_temp) + "C",
#             '(BME280) Humidity: ' : attemptCall(bme280.get_humidity) + "rh",
#             '(BME280) Pressure: ' : attemptCall(bme280.get_pressure) + "hP"
#             } # Get Values from Sensors

#         with open("/home/mason35/Desktop/Enviroment/Outputs/OutputData " + str(time.ctime(start_time)), "a") as f:
#             json.dump(newDictionary,f,indent=4) # Dump the values to the Json File

#         print(f"Succseful Read at {current_Time} with {errors_on_scan} Errors!")
#         time.sleep(INTERVAL_TIME)
# main()