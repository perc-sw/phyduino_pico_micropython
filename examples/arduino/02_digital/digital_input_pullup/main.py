# Reads a pushbutton on D2 using the pin's pull-up resistor, so no other parts
# are needed, prints its state and lights the on-board LED while it is pressed.
#
# Connect a pushbutton between D2 and GND. The pull-up holds D2 at 1 while the
# button is open, so the logic is inverted: pressed reads 0.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = None  # the button's pin; setup() fills this in


def setup():
    global button  # change the button variable above, not a new one inside setup()
    button = mcu.pin("D2", "in", pull="up")  # D2 as an input, held at 1 until pressed


def loop():
    state = button.value()  # 0 while pressed (the button connects D2 to GND), 1 when not
    print(state)
    mcu.led.value(not state)  # "not" swaps 0 and 1, so the LED is on while pressed
    time.sleep(0.1)  # ten readings a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
