# Prints the state of a pushbutton on D2, 1 when pressed and 0 when not, ten
# times a second.
#
# Connect a pushbutton between D2 and 3.3 V. The pin's pull-down resistor
# holds D2 at 0 while the button is open.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = None  # the button's pin; setup() fills this in


def setup():
    global button  # change the button variable above, not a new one inside setup()
    button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed


def loop():
    print(button.value())  # 1 while the button is pressed, 0 when it is not
    time.sleep(0.1)  # ten readings a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
