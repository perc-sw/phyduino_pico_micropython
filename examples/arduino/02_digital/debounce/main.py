# Toggles the on-board LED each time a pushbutton on D2 is pressed, ignoring
# the contact bounce that makes one press look like several.
#
# A new reading only counts once it has stayed the same for DEBOUNCE_MS.
# Connect a pushbutton between D2 and 3.3 V; the pull-down holds D2 at 0
# while the button is open.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUTTON_PIN = 2  # the pushbutton is on D2
DEBOUNCE_MS = 50  # how long a reading must stay the same to count, in milliseconds

led_state = HIGH  # HIGH = LED on, LOW = off
button_state = LOW  # the steady reading
last_reading = LOW  # the reading on the previous pass
last_change_ms = 0  # when the reading last changed


def setup():
    pinMode(BUTTON_PIN, INPUT_PULLDOWN)  # D2 as an input, held LOW until pressed
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output
    digitalWrite(LED_BUILTIN, led_state)  # start with the LED on


def loop():
    # loop() changes all of these, so it needs the ones above.
    global led_state, button_state, last_reading, last_change_ms
    reading = digitalRead(BUTTON_PIN)  # HIGH while pressed, LOW when not
    if reading != last_reading:
        last_change_ms = millis()  # it changed (or bounced): start the wait again
    # Only believe the reading once it has stayed the same for DEBOUNCE_MS.
    if millis() - last_change_ms > DEBOUNCE_MS:
        if reading != button_state:  # a real change
            button_state = reading
            if button_state == HIGH:  # only act on a press, not a release
                led_state = HIGH if led_state == LOW else LOW  # swap on and off
    digitalWrite(LED_BUILTIN, led_state)
    last_reading = reading  # compare against this next time


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
