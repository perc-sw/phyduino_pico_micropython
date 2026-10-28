# Prints the state of a pushbutton on D2, 1 when pressed and 0 when not, ten
# times a second.
#
# Connect a pushbutton between D2 and 3.3 V. The pin's pull-down resistor
# holds D2 at 0 while the button is open.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUTTON_PIN = 2  # the pushbutton is on D2


def setup():
    pinMode(BUTTON_PIN, INPUT_PULLDOWN)  # D2 as an input, held at 0 until pressed


def loop():
    print(digitalRead(BUTTON_PIN))  # 1 while the button is pressed, 0 when it is not
    delay(100)  # ten readings a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
