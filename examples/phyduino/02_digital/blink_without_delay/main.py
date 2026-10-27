# Blinks the on-board LED once a second without time.sleep(), so the loop is
# free to do other work between changes. Each pass checks how long it has been
# since the last change with time.ticks_ms() and time.ticks_diff().

import time  # ticks_ms() and ticks_diff() for timing

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

INTERVAL_MS = 500  # time between changes, in milliseconds

mcu.led.off()  # start with the LED off
previous_ms = time.ticks_ms()  # the time of the last change: milliseconds since the board started

while True:  # repeats until you press Ctrl-C (or Stop in your editor)
    now = time.ticks_ms()  # the time now
    # ticks_diff() gives the time between two ticks_ms() readings. Always use it
    # rather than now - previous_ms: the count wraps round to 0 after a while.
    if time.ticks_diff(now, previous_ms) >= INTERVAL_MS:
        previous_ms = now  # remember when this change happened
        mcu.led.toggle()  # on if it was off, off if it was on
    # Nothing here waits, so other work can go here and still run every pass.
