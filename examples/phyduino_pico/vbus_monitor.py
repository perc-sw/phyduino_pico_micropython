# Prints the USB-C supply voltage (VBUS) and the RP2040's temperature once a
# second. VBUS is about 5 V from a computer; a USB-PD charger can raise it
# (see usb_pd_power.py). VBUS is also on the header's VIN pin.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>


def setup():
    pass  # nothing to set up


def loop():
    # "%.2f" shows two decimal places, "%.1f" one.
    print("VBUS %.2f V    CPU %.1f C" % (mcu.vbus_volts(), mcu.cpu_temperature()))
    time.sleep(1)  # once a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
