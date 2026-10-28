# Turns the on-board LED on when it receives "H" and off when it receives "L"
# from the computer. Type the letters in the REPL terminal (PyCharm's REPL
# or mpremote) while the script runs.
#
# sys.stdin.read(1) waits for the next character, so loop() pauses until one
# arrives.

import sys  # sys.stdin: characters typed in the terminal

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output
    digitalWrite(LED_BUILTIN, LOW)  # start with the LED off
    print("Type H to turn the LED on, L to turn it off.")


def loop():
    char = sys.stdin.read(1)  # wait for one character from the terminal
    if char == "H":
        digitalWrite(LED_BUILTIN, HIGH)
    elif char == "L":
        digitalWrite(LED_BUILTIN, LOW)
    # Any other character is ignored.


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
