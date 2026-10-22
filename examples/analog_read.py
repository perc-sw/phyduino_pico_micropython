# Reads all six analogue pins as 12-bit codes (0-4095), twice a second.
#
# A0-A2: 0 = 0 V, 4095 = 3.3 V (RP2040 ADC).
# A3-A5: 0 = 0 V, 4095 = 2.048 V (on-board MAX11635 ADC).
# Connect a potentiometer wiper (ends on GND and 3.3 V) to any pin to see it
# change; keep A3-A5 at or below 2.048 V. Unconnected pins drift.

import time

import phyduino as pd

NAMES = ("A0", "A1", "A2", "A3", "A4", "A5")

while True:
    print("  ".join("%s=%4d" % (name, pd.analog_read(name)) for name in NAMES))
    time.sleep(0.5)
