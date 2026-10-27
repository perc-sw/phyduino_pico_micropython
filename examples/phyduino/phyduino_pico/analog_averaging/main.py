# Shows how averaging steadies a reading. For each setting, takes 100
# readings of A0 and A3 and prints the lowest, the highest and the spread
# between them (in ADC steps), then waits 5 seconds and starts again.
# Connect a steady voltage, e.g. a potentiometer wiper, to A0 (0-3.3 V) and
# A3 (0-2.048 V), or leave them as they are.
#
# analog_averaging() applies to every analogue pin: A3-A5 average in the
# external ADC itself, A0-A2 take the samples one after another.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

READINGS = 100  # readings taken for each setting


def spread(name):
    """Takes READINGS readings of one pin; returns the lowest, the highest and the gap."""
    values = [mcu.analog_read(name) for _ in range(READINGS)]  # a list of 100 readings
    return min(values), max(values), max(values) - min(values)


while True:  # repeats until you press Ctrl-C (or Stop in your editor)
    for samples in (1, 4, 8, 16, 32):  # each averaging setting in turn
        mcu.analog_averaging(samples)  # every reading is now the average of this many samples
        for name in ("A0", "A3"):  # A0: RP2040 ADC; A3: on-board MAX11635
            low, high, width = spread(name)  # the three numbers spread() returns
            print("averaging %2d  %s  lowest %4d  highest %4d  spread %3d" % (samples, name, low, high, width))
    mcu.analog_averaging(1)  # back to single readings
    print()  # a blank line between runs
    time.sleep(5)  # start again in five seconds
