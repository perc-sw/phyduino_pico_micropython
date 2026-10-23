# Counts presses of a pushbutton on D2 and lights the on-board LED on every
# fourth press. It acts on the change from released to pressed (an edge),
# not on the button being held down.
#
# Connect a pushbutton between D2 and 3.3 V; the pull-down holds D2 at 0
# while the button is open.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

button = None  # the button's pin; setup() fills this in
presses = 0  # how many times the button has been pressed
last_state = 0  # the reading on the previous pass


def setup():
    global button  # change the button variable above, not a new one inside setup()
    button = mcu.pin("D2", "in", pull="down")  # D2 as an input, held at 0 until pressed
    mcu.led.off()  # start with the LED off


def loop():
    global presses, last_state  # loop() changes both, so it needs the ones above
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
    mcu.led.value(presses % 4 == 0)  # % is the remainder: on after 4, 8, 12, ... presses


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
