# Prints the USB-C supply voltage (VBUS) and the RP2040's temperature once a
# second. VBUS is about 5 V from a computer; a USB-PD charger can raise it
# (see usb_pd_power.py). VBUS is also on the header's VIN pin.

import time

import phyduino as pd

while True:
    print("VBUS %.2f V    CPU %.1f C" % (pd.vbus_volts(), pd.cpu_temperature()))
    time.sleep(1)
