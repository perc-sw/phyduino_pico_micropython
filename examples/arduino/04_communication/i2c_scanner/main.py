# Lists the addresses of the I2C devices on SDA (D18) and SCL (D19), every
# 5 seconds, so a module can be plugged in while it runs.
#
# The board has no pull-up resistors on these pins. Most sensor modules
# include them; otherwise fit 4.7 kOhm resistors from SDA and SCL to 3.3 V.
# The on-board USB-PD controller is on a separate bus and does not appear.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...
import phyduino as mcu  # the Phyduino Pico library, for mcu.i2c() in place of Arduino's Wire

bus = None  # the I2C bus; setup() fills this in


def setup():
    global bus  # change the bus variable above, not a new one inside setup()
    bus = mcu.i2c()  # I2C on SDA (D18) and SCL (D19)


def loop():
    found = bus.scan()  # a list of the addresses that answered, e.g. [60, 118]
    if found:  # an empty list counts as false
        # "0x%02X" shows each address in hexadecimal, as datasheets do, e.g. 0x3C.
        print("Found:", ", ".join("0x%02X" % address for address in found))
    else:
        print("No devices found. Check the wiring and the pull-up resistors.")
    delay(5000)  # scan again in five seconds


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
