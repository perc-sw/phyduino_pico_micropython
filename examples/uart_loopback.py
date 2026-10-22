# Sends a message out of UART0 and reads it back. Connect a jumper wire from
# D1 (TX) to D0 (RX) first; without it, nothing comes back.

import time

import phyduino as pd

serial = pd.uart(0, 115200)

for count in range(5):
    message = "hello %d" % count
    serial.write(message)
    time.sleep(0.05)
    received = serial.read()
    print("sent %r, received %r" % (message, received.decode() if received else None))
    time.sleep(0.5)
