# Blinks the on-board green LED once a second.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output


def loop():
    digitalWrite(LED_BUILTIN, HIGH)  # LED on
    delay(500)  # wait half a second
    digitalWrite(LED_BUILTIN, LOW)  # LED off
    delay(500)  # wait half a second, so one on-off cycle takes a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
