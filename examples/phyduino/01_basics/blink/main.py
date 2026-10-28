# Blinks the on-board green LED once a second.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

mcu.led.off()  # start with the LED off

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    mcu.led.toggle()  # on if it was off, off if it was on
    time.sleep(0.5)  # wait half a second, so one on-off cycle takes a second
