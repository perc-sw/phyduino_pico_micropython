# Prints the state of a pushbutton on D2, 1 when pressed and 0 when not, ten
# times a second.
#
# Connect a pushbutton between D2 and 3.3 V. The pin's pull-down resistor
# holds D2 at 0 while the button is open.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    print(button.value())  # 1 while the button is pressed, 0 when it is not
    time.sleep(0.1)  # ten readings a second
