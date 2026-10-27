# Sends a numbered message out of UART0 and reads it back, twice a second.
# Connect a jumper wire from D1 (TX) to D0 (RX) first; without it, nothing
# comes back.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...
import phyduino as mcu  # the Phyduino Pico library, for mcu.uart() in place of Arduino's Serial1

serial = None  # the serial port; setup() fills this in
count = 0  # the number in the next message


def setup():
    global serial  # change the serial variable above, not a new one inside setup()
    serial = mcu.uart(0, 115200)  # UART0: TX on D1, RX on D0, 115200 bits per second


def loop():
    global count  # loop() changes it, so it needs the one above
    message = "hello %d" % count  # e.g. "hello 0"
    serial.write(message)  # send it out of D1
    delay(50)  # give it time to arrive back on D0
    received = serial.read()  # everything that has arrived, as bytes; None if nothing
    # decode() turns the bytes back into text; %r shows the quotes, so None stands out.
    print("sent %r, received %r" % (message, received.decode() if received else None))
    count += 1  # a new number next time
    delay(500)  # twice a second


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
