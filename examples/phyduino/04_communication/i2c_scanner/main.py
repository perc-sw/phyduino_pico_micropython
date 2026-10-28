# Lists the addresses of the I2C devices on SDA (D18) and SCL (D19), every
# 5 seconds, so a module can be plugged in while it runs.
#
# The board has no pull-up resistors on these pins. Most sensor modules
# include them; otherwise fit 4.7 kOhm resistors from SDA and SCL to 3.3 V.
# The on-board USB-PD controller is on a separate bus and does not appear.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

bus = mcu.i2c()  # I2C on SDA (D18) and SCL (D19)

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    found = bus.scan()  # a list of the addresses that answered, e.g. [60, 118]
    if found:  # an empty list counts as false
        # "0x%02X" shows each address in hexadecimal, as datasheets do, e.g. 0x3C.
        print("Found:", ", ".join("0x%02X" % address for address in found))
    else:
        print("No devices found. Check the wiring and the pull-up resistors.")
    time.sleep(5)  # scan again in five seconds
