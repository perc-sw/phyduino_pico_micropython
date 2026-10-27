# Shows how averaging steadies a reading. For each setting, takes 100
# readings of A0 and A3 and prints the lowest, the highest and the spread
# between them (in ADC steps), then waits 5 seconds and starts again.
# Connect a steady voltage, e.g. a potentiometer wiper, to A0 (0-3.3 V) and
# A3 (0-2.048 V), or leave them as they are.
#
# Arduino has no averaging setting, so this uses mcu.analog_averaging(). It
# applies to every analogue pin: A3-A5 average in the external ADC itself,
# A0-A2 take the samples one after another.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...
import phyduino as mcu  # the Phyduino Pico library, for mcu.analog_averaging()

READINGS = 100  # readings taken for each setting


def spread(pin):
    """Takes READINGS readings of one pin; returns the lowest, the highest and the gap."""
    values = [analogRead(pin) for _ in range(READINGS)]  # a list of 100 readings
    return min(values), max(values), max(values) - min(values)


def setup():
    analogReadResolution(12)  # analogRead() gives 0-4095, the ADCs' own steps


def loop():
    for samples in (1, 4, 8, 16, 32):  # each averaging setting in turn
        mcu.analog_averaging(samples)  # every reading is now the average of this many samples
        for pin in (A0, A3):  # A0: RP2040 ADC; A3: on-board MAX11635
            low, high, width = spread(pin)  # the three numbers spread() returns
            print("averaging %2d  %s  lowest %4d  highest %4d  spread %3d" % (samples, pin, low, high, width))
    mcu.analog_averaging(1)  # back to single readings
    print()  # a blank line between runs
    delay(5000)  # start again in five seconds


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
