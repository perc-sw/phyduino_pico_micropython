# Lights the on-board LED while a pushbutton on D2 is pressed.
#
# Connect a pushbutton between D2 and 3.3 V. The pin's pull-down resistor
# holds D2 at 0 while the button is open.

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    mcu.led.value(button.value())  # the button reads 1 while pressed; the LED is on at 1, off at 0
