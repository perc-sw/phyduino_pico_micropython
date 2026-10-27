# Prints the reading on A0, one number per line, 50 times a second, for a
# serial plotter to draw as a graph.
#
# Connect a potentiometer wiper or sensor to A0 (0-3.3 V). Any serial plotter
# that reads one number per line can show it; close PyCharm's REPL or mpremote
# first so the port is free.

import time  # sleep_ms() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

while True:  # repeats until you press Ctrl-C (or Stop in your editor)
    print(mcu.analog_read("A0"))  # one number per line, 0-4095, for the plotter
    time.sleep_ms(20)  # 20 ms apart: 50 readings a second
