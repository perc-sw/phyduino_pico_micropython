# Counts presses of a pushbutton on D2 and lights the on-board LED at the
# start and on every fourth press. It acts on the change from released to pressed (an edge),
# not on the button being held down.
#
# Connect a pushbutton between D2 and 3.3 V; the pull-down holds D2 at 0
# while the button is open.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed
mcu.led.off()  # LED off until the loop's first pass turns it on (0 presses)
presses = 0  # how many times the button has been pressed
last_state = 0  # the reading on the previous pass

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    state = button.value()  # 1 while pressed, 0 when not
    if state != last_state:  # it has changed since the last pass: an edge
        if state == 1:  # released to pressed
            presses += 1
            print("on")
            print("number of button pushes:", presses)
        else:  # pressed to released
            print("off")
        time.sleep(0.05)  # let the contacts settle (bounce) before reading again
    last_state = state  # compare against this next time
    mcu.led.value(presses % 4 == 0)  # % is the remainder: on at 0, 4, 8, ... presses
