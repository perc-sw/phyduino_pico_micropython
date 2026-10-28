# The smallest program: set-up code goes in setup(), which runs once, and the
# main code goes in loop(), which runs over and over. Copy this file to start
# a new program.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    pass  # put your set-up code here, to run once ("pass" means do nothing)


def loop():
    pass  # put your main code here, to run repeatedly


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
