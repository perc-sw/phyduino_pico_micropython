# Shows how averaging steadies a reading. For each setting, takes 100
# readings of A0 and A3 and prints the lowest, the highest and the spread
# between them (in ADC steps). Connect a steady voltage, e.g. a potentiometer
# wiper, to A0 (0-3.3 V) and A3 (0-2.048 V), or leave them as they are.
#
# analog_averaging() applies to every analogue pin: A3-A5 average in the
# external ADC itself, A0-A2 take the samples one after another.

import phyduino as pd

READINGS = 100


def spread(name):
    values = [pd.analog_read(name) for _ in range(READINGS)]
    return min(values), max(values), max(values) - min(values)


for samples in (1, 4, 8, 16, 32):
    pd.analog_averaging(samples)
    for name in ("A0", "A3"):
        low, high, width = spread(name)
        print("averaging %2d  %s  lowest %4d  highest %4d  spread %3d" % (samples, name, low, high, width))
pd.analog_averaging(1)
