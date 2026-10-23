# Learns the range of a sensor on A0 during the first five seconds, then sets
# the on-board LED's brightness from where each reading falls in that range.
#
# Connect a sensor (e.g. a light-dependent resistor divider) to A0. While the
# LED is on at the start, give the sensor its lowest and highest values, e.g.
# cover it and then shine a light on it.

import time  # ticks_ms(), ticks_diff() and sleep_ms() for timing

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

CALIBRATION_MS = 5000  # how long to learn the range for, in milliseconds

led = None  # the LED's PWM output; setup() fills this in
sensor_min = 4095  # start the wrong way round so the first readings replace them
sensor_max = 0


def setup():
    global led, sensor_min, sensor_max  # setup() changes all three
    mcu.led.on()  # the LED is on while calibrating
    start = time.ticks_ms()  # when calibration began
    # Keep reading until CALIBRATION_MS has passed, remembering the lowest and highest.
    while time.ticks_diff(time.ticks_ms(), start) < CALIBRATION_MS:
        value = mcu.analog_read("A0")  # 0-4095
        sensor_min = min(sensor_min, value)  # the lowest so far
        sensor_max = max(sensor_max, value)  # the highest so far
        time.sleep_ms(10)
    mcu.led.off()  # calibration finished
    print("range:", sensor_min, "-", sensor_max)
    led = mcu.pwm("LED")  # Puts the LED's pin into PWM mode and saves the control variable to the 'led' variable.


def loop():
    value = mcu.analog_read("A0")
    span = max(sensor_max - sensor_min, 1)  # the width of the range; at least 1, so no divide by 0
    value = min(max(value, sensor_min), sensor_max)  # keep in the range, like constrain()
    led.duty_u16((value - sensor_min) * 65535 // span)  # bottom of the range = off, top = fully on
    time.sleep_ms(10)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
