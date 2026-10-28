# Toggles the on-board LED each time a pushbutton on D2 is pressed, ignoring
# the contact bounce that makes one press look like several.
#
# A new reading only counts once it has stayed the same for DEBOUNCE_MS.
# Connect a pushbutton between D2 and 3.3 V; the pull-down holds D2 at 0
# while the button is open.

import time  # ticks_ms() and ticks_diff() for timing

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

DEBOUNCE_MS = 50  # how long a reading must stay the same to count, in milliseconds

button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed
mcu.led.on()  # start with the LED on
button_state = 0  # the steady reading
last_reading = 0  # the reading on the previous pass
last_change_ms = time.ticks_ms()  # when the reading last changed

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    reading = button.value()  # 1 while pressed, 0 when not
    if reading != last_reading:
        last_change_ms = time.ticks_ms()  # it changed (or bounced): start the wait again
    # Only believe the reading once it has stayed the same for DEBOUNCE_MS.
    if time.ticks_diff(time.ticks_ms(), last_change_ms) > DEBOUNCE_MS:
        if reading != button_state:  # a real change
            button_state = reading
            if button_state == 1:  # only act on a press, not a release
                mcu.led.toggle()  # swap on and off
    last_reading = reading  # compare against this next time
