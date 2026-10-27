# Lights the on-board LED while a pushbutton on D2 is pressed.
#
# Connect a pushbutton between D2 and 3.3 V. The pin's pull-down resistor
# holds D2 at 0 while the button is open.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUTTON_PIN = 2  # the pushbutton is on D2


def setup():
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output
    pinMode(BUTTON_PIN, INPUT_PULLDOWN)  # D2 as an input, held LOW until pressed


def loop():
    if digitalRead(BUTTON_PIN) == HIGH:  # HIGH while pressed
        digitalWrite(LED_BUILTIN, HIGH)  # LED on
    else:
        digitalWrite(LED_BUILTIN, LOW)  # LED off


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
