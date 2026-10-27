# Lights the on-board LED while a pushbutton on D2 is pressed.
#
# Connect a pushbutton between D2 and 3.3 V. The pin's pull-down resistor
# holds D2 at 0 while the button is open.

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = None  # the button's pin; setup() fills this in


def setup():
    global button  # change the button variable above, not a new one inside setup()
    button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed


def loop():
    # The button reads 1 while pressed and 0 when not; the LED is on at 1, off at 0.
    mcu.led.value(button.value())


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
