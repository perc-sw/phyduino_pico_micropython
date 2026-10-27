# Reads all six analogue pins with analogRead() (0-1023), twice a second.
#
# A0-A2: 0 = 0 V, 1023 = 3.3 V (RP2040 ADC).
# A3-A5: 0 = 0 V, 1023 = 2.048 V (on-board MAX11635 ADC).
# Connect a potentiometer wiper (ends on GND and 3.3 V) to any pin to see it
# change; keep A3-A5 at or below 2.048 V. Unconnected pins drift.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

PINS = (A0, A1, A2, A3, A4, A5)  # the pins to read, in order


def setup():
    pass  # analogue pins need no set-up


def loop():
    # Read each pin and print them on one line, e.g. "A0= 512  A1=   0 ...".
    # "%s=%4d" puts the name, then the reading right-aligned in 4 characters.
    print("  ".join("%s=%4d" % (pin, analogRead(pin)) for pin in PINS))
    delay(500)  # wait half a second before the next line


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
