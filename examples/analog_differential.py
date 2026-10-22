# Measures the voltage between two analogue pins, e.g. across a resistor or a
# sensor bridge, twice a second.
#
# A3 - A4: true differential. The on-board ADC samples both pins at the same
#   instant, so noise common to both cancels. Range +/-1024 mV in 0.5 mV steps
#   (a larger difference is measured as two separate readings).
# A0 - A1: computed from readings taken one after the other.
#   Fine for slow signals, but noise on both pins does not cancel.
#
# Keep every pin between 0 V and its full scale (A0-A2: 3.3 V, A3-A5: 2.048 V).

import time

import phyduino as pd

pd.analog_averaging(16)  # steadier readings

while True:
    print("A3 - A4: %7.1f mV    A0 - A1: %7.1f mV" % (
        pd.analog_differential_millivolts("A3", "A4"),
        pd.analog_differential_millivolts("A0", "A1")))
    time.sleep(0.5)
