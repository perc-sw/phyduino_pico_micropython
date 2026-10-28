# Prints a running average of the last 10 readings of A0, which steadies a
# noisy signal. Each new reading replaces the oldest one.
#
# Connect a potentiometer wiper or sensor to A0 (0-3.3 V). For averaging done
# by the board itself, see phyduino_pico/analog_averaging/.

import time  # sleep_ms() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

NUM_READINGS = 10  # how many readings to average; more is smoother but slower to follow

readings = [0] * NUM_READINGS  # the last 10 readings, all 0 to begin with
index = 0  # where the next reading goes in the list
total = 0  # the sum of the readings in the list

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    total -= readings[index]  # take the oldest reading out of the sum
    readings[index] = mcu.analog_read("A0")  # replace it with a new one
    total += readings[index]  # and add that to the sum
    index = (index + 1) % NUM_READINGS  # move along; % wraps back to 0 after the end
    print(total // NUM_READINGS)  # the average
    time.sleep_ms(1)  # a short pause between readings
