Re# Reads all six analogue pins as 12-bit codes (0-4095), twice a second.
#
# A0-A2: 0 = 0 V, 4095 = 3.3 V (RP2040 ADC).
# A3-A5: 0 = 0 V, 4095 = 2.048 V (on-board MAX11635 ADC).
# Connect a potentiometer wiper (ends on GND and 3.3 V) to any pin to see it
# change; keep A3-A5 at or below 2.048 V. Unconnected pins drift.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

NAMES = ("A0", "A1", "A2", "A3", "A4", "A5")  # the pins to read, in order


def setup():
    pass  # analogue pins need no set-up


def loop():
    # Read each pin and print them on one line, e.g. "A0=2048  A1=   3 ...".
    # "%s=%4d" puts the name, then the reading right-aligned in 4 characters.
    print("  ".join("%s=%4d" % (name, mcu.analog_read(name)) for name in NAMES))
    time.sleep(0.5)  # wait half a second before the next line


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
