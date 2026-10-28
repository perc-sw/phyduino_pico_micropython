# Blinks the on-board LED once a second without delay(), so loop() is free to
# do other work between changes. Each pass checks how long it has been since
# the last change with millis().

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

INTERVAL_MS = 500  # time between changes, in milliseconds

led_state = LOW  # the LED's level: LOW = off, HIGH = on
previous_ms = 0  # the time of the last change


def setup():
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output


def loop():
    global led_state, previous_ms  # loop() changes both, so it needs the ones above
    now = millis()  # milliseconds since the board started
    if now - previous_ms >= INTERVAL_MS:  # millis() never wraps round, so plain subtraction works
        previous_ms = now  # remember when this change happened
        led_state = HIGH if led_state == LOW else LOW  # swap on and off
        digitalWrite(LED_BUILTIN, led_state)
    # Nothing here waits, so other work can go here and still run every pass.


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
