# Prints the voltage on every analogue pin, in millivolts, twice a second.
#
# analogRead() gives 0-1024 steps of the pin's full scale (3.3 V for A0-A2,
# 2.048 V for A3-A5), so each pin is scaled with its own, and the numbers can
# be compared directly.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

PINS = (A0, A1, A2, A3, A4, A5)  # the pins to read, in order
FULL_SCALE_MV = (3300, 3300, 3300, 2048, 2048, 2048)  # each pin's full scale, in millivolts


def setup():
    pass  # analogue pins need no set-up


def loop():
    # zip() pairs each pin with its full scale; reading * full scale / 1024 is millivolts.
    # "%.1f" shows each number with one decimal place, e.g. 1650.0.
    print(" ".join("%.1f" % (analogRead(pin) * mv / 1024) for pin, mv in zip(PINS, FULL_SCALE_MV)))
    delay(500)  # wait half a second before the next line


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
