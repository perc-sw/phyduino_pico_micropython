# USB-PD power: asks a USB-PD charger for up to MAX_VOLTS, then prints the
# board's profiles, the contract and the measured VBUS once a second.
#
# A charger takes the only USB-C port, so there is no USB connection to the
# computer while it is plugged in. Copy this main.py to the board so it runs
# by itself, and watch the output on UART0 (TX on D1, 115200 baud)
# with a USB-serial adapter. The green POK2 LED lights for the second
# profile (9 V), POK3 for the third (the 12, 15 or 20 V of MAX_VOLTS).
#
# VBUS also feeds the VIN pin, so VIN follows the contract: disconnect
# anything on VIN that can't take the voltage you ask for.
# The request lasts until the board loses power.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

MAX_VOLTS = 9  # 5, 9, 12, 15 or 20

serial = mcu.uart(0)  # UART0: TX on D1, 115200 bits per second


def report(text):
    """Prints text, and sends it out of UART0 too, as USB is taken by the charger."""
    print(text)
    serial.write(text + "\r\n")  # "\r\n" ends the line for a serial terminal


usb = mcu.usb_pd()  # the on-board STUSB4500 USB-PD controller
usb.request(MAX_VOLTS)  # ask the charger for up to MAX_VOLTS
# profiles() lists the (volts, amps) the board offers; "%g" drops trailing zeros.
report("Profiles: " + ", ".join("%g V %g A" % p for p in usb.profiles()))

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    volts, amps = usb.contract()  # what the charger agreed to supply
    position = usb.contract_position()  # which charger offer is in use; 0 if none
    if position:  # 0 counts as false
        report("Contract: offer %d, %.2f A    VBUS %.2f V" % (position, amps, volts))
    else:
        report("No PD contract (plain USB)    VBUS %.2f V" % volts)
    time.sleep(1)  # once a second
