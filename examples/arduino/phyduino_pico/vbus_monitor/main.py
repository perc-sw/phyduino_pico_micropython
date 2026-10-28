# Prints the USB-C supply voltage (VBUS) and the RP2040's temperature once a
# second. VBUS is about 5 V from a computer; a USB-PD charger can raise it
# (see phyduino_pico/usb_pd_power/). VBUS is also on the header's VIN pin.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...
import phyduino as mcu  # the Phyduino Pico library, for mcu.vbus_volts() and mcu.cpu_temperature()


def setup():
    pass  # nothing to set up


def loop():
    # "%.2f" shows two decimal places, "%.1f" one.
    print("VBUS %.2f V    CPU %.1f C" % (mcu.vbus_volts(), mcu.cpu_temperature()))
    delay(1000)  # once a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
