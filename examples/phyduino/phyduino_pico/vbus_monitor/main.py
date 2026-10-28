# Prints the USB-C supply voltage (VBUS) and the RP2040's temperature once a
# second. VBUS is about 5 V from a computer; a USB-PD charger can raise it
# (see phyduino_pico/usb_pd_power/). VBUS is also on the header's VIN pin.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    # "%.2f" shows two decimal places, "%.1f" one.
    print("VBUS %.2f V    CPU %.1f C" % (mcu.vbus_volts(), mcu.cpu_temperature()))
    time.sleep(1)  # once a second
