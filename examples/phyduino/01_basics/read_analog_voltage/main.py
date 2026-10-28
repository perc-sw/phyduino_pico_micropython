# Prints the voltage on every analogue pin, in millivolts, twice a second.
#
# The library scales each pin with its own full scale (3.3 V for A0-A2,
# 2.048 V for A3-A5), so the numbers can be compared directly.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

NAMES = ("A0", "A1", "A2", "A3", "A4", "A5")  # the pins to read, in order

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    # Read each pin in millivolts and print them on one line.
    # "%.1f" shows each number with one decimal place, e.g. 1650.0.
    print(" ".join("%.1f" % mcu.analog_millivolts(name) for name in NAMES))
    time.sleep(0.5)  # wait half a second before the next line
