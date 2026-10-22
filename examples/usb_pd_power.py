# USB-PD power: asks a USB-PD charger for up to MAX_VOLTS, then prints the
# board's profiles, the contract and the measured VBUS once a second.
#
# A charger takes the only USB-C port, so there is no USB connection to the
# computer while it is plugged in. Save this file as main.py on the board so
# it runs by itself, and watch the output on UART0 (TX on D1, 115200 baud)
# with a USB-serial adapter. The green POK2 LED lights at 9 V, POK3 at 20 V.
#
# VBUS also feeds the VIN pin, so VIN follows the contract: disconnect
# anything on VIN that can't take the voltage you ask for.
# The request lasts until the board loses power.

import time

import phyduino as pd

MAX_VOLTS = 9  # 5, 9, 12, 15 or 20

serial = pd.uart(0)


def report(text):
    print(text)
    serial.write(text + "\r\n")


usb = pd.usb_pd()
usb.request(MAX_VOLTS)
report("Profiles: " + ", ".join("%g V %g A" % p for p in usb.profiles()))

while True:
    volts, amps = usb.contract()
    position = usb.contract_position()
    if position:
        report("Contract: offer %d, %.2f A    VBUS %.2f V" % (position, amps, volts))
    else:
        report("No PD contract (plain USB)    VBUS %.2f V" % volts)
    time.sleep(1)
