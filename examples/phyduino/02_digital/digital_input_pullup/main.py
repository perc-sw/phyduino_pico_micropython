# Reads a pushbutton on D2 using the pin's pull-up resistor, so no other parts
# are needed, prints its state and lights the on-board LED while it is pressed.
#
# Connect a pushbutton between D2 and GND. The pull-up holds D2 at 1 while the
# button is open, so the logic is inverted: pressed reads 0.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = mcu.pin("D2", "in", pull="up")  # D2 as an input, held at 1 until pressed

while True:  # repeats until you press Ctrl-C (or Stop in your editor)
    state = button.value()  # 0 while pressed (the button connects D2 to GND), 1 when not
    print(state)
    mcu.led.value(not state)  # "not" swaps 0 and 1, so the LED is on while pressed
    time.sleep(0.1)  # ten readings a second
