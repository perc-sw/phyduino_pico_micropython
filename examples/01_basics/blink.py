# Blinks the on-board green LED once a second.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>


def setup():
    mcu.led.off()  # start with the LED off


def loop():
    mcu.led.toggle()  # on if it was off, off if it was on
    time.sleep(0.5)  # wait half a second, so one on-off cycle takes a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
