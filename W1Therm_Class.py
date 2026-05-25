
from w1thermsensor import W1ThermSensor, Unit

sensor = W1ThermSensor()


def get_temp_F():
    return "%0.1f" % sensor.get_temperature(Unit.DEGREES_F)

def get_temp_C():
    return "%0.1f" % sensor.get_temperature(Unit.DEGREES_C)

def get_temp_K():
    return "%0.1f" % sensor.get_temperature(Unit.KELVIN)

print("W1Therm Initialized!")

