# Sends a numbered message out of UART0 and reads it back, twice a second.
# Connect a jumper wire from D1 (TX) to D0 (RX) first; without it, nothing
# comes back.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

serial = mcu.uart(0, 115200)  # UART0: TX on D1, RX on D0, 115200 bits per second
count = 0  # the number in the next message

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    message = "hello %d" % count  # e.g. "hello 0"
    serial.write(message)  # send it out of D1
    time.sleep(0.05)  # give it time to arrive back on D0
    received = serial.read()  # everything that has arrived, as bytes; None if nothing
    # decode() turns the bytes back into text; %r shows the quotes, so None stands out.
    print("sent %r, received %r" % (message, received.decode() if received else None))
    count += 1  # a new number next time
    time.sleep(0.5)  # twice a second
