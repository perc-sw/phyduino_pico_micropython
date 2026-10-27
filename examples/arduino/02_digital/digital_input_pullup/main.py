# Reads a pushbutton on D2 using the pin's pull-up resistor, so no other parts
# are needed, prints its state and lights the on-board LED while it is pressed.
#
# Connect a pushbutton between D2 and GND. The pull-up holds D2 at 1 while the
# button is open, so the logic is inverted: pressed reads 0.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUTTON_PIN = 2  # the pushbutton is on D2


def setup():
    pinMode(BUTTON_PIN, INPUT_PULLUP)  # D2 as an input, held HIGH until pressed
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output


def loop():
    state = digitalRead(BUTTON_PIN)  # LOW while pressed (the button connects D2 to GND), HIGH when not
    print(state)
    if state == LOW:  # pressed
        digitalWrite(LED_BUILTIN, HIGH)  # LED on
    else:
        digitalWrite(LED_BUILTIN, LOW)  # LED off
    delay(100)  # ten readings a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
