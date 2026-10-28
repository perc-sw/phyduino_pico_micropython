# Learns the range of a sensor on A0 during the first five seconds, then sets
# the on-board LED's brightness from where each reading falls in that range.
#
# Connect a sensor (e.g. a light-dependent resistor divider) to A0. While the
# LED is on at the start, give the sensor its lowest and highest values, e.g.
# cover it and then shine a light on it.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

SENSOR_PIN = A0  # the sensor is on A0
CALIBRATION_MS = 5000  # how long to learn the range for, in milliseconds

sensor_min = 1023  # start the wrong way round so the first readings replace them
sensor_max = 0


def setup():
    global sensor_min, sensor_max  # setup() changes both
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output
    digitalWrite(LED_BUILTIN, HIGH)  # the LED is on while calibrating
    start = millis()  # when calibration began
    # Keep reading until CALIBRATION_MS has passed, remembering the lowest and highest.
    while millis() - start < CALIBRATION_MS:
        value = analogRead(SENSOR_PIN)  # 0-1023
        sensor_min = min(sensor_min, value)  # the lowest so far
        sensor_max = max(sensor_max, value)  # the highest so far
        delay(10)
    digitalWrite(LED_BUILTIN, LOW)  # calibration finished
    print("range:", sensor_min, "-", sensor_max)
    sensor_max = max(sensor_max, sensor_min + 1)  # at least 1 apart, so map() never divides by 0


def loop():
    value = analogRead(SENSOR_PIN)
    value = constrain(value, sensor_min, sensor_max)  # keep it in the calibrated range
    value = map(value, sensor_min, sensor_max, 0, 255)  # bottom of the range = 0, top = 255
    analogWrite(LED_BUILTIN, value)  # off at the bottom, fully on at the top
    delay(10)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
