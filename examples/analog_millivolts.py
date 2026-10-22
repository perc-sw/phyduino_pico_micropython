# Prints the voltage on every analogue pin, in millivolts, twice a second.
#
# The library scales each pin with its own full scale (3.3 V for A0-A2,
# 2.048 V for A3-A5), so the numbers can be compared directly.

import time

import phyduino as pd

NAMES = ("A0", "A1", "A2", "A3", "A4", "A5")

while True:
    print(" ".join("%.1f" % pd.analog_millivolts(name) for name in NAMES))
    time.sleep(0.5)
