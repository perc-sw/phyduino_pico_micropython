# Lists the addresses of the I2C devices on SDA (D18) and SCL (D19).
#
# The board has no pull-up resistors on these pins. Most sensor modules
# include them; otherwise fit 4.7 kOhm resistors from SDA and SCL to 3.3 V.
# The on-board USB-PD controller is on a separate bus and does not appear.

import phyduino as pd

bus = pd.i2c()
found = bus.scan()
if found:
    print("Found:", ", ".join("0x%02X" % address for address in found))
else:
    print("No devices found. Check the wiring and the pull-up resistors.")
