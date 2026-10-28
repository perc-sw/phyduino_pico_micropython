# Prints the reading on A0, one number per line, 50 times a second, for a
# serial plotter to draw as a graph.
#
# Connect a potentiometer wiper or sensor to A0 (0-3.3 V). Any serial plotter
# that reads one number per line can show it; close PyCharm's REPL or mpremote
# first so the port is free.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    pass  # analogue pins need no set-up


def loop():
    print(analogRead(A0))  # one number per line, 0-1023, for the plotter
    delay(20)  # 20 ms apart: 50 readings a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
