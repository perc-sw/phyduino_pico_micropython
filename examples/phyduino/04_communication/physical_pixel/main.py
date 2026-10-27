# Turns the on-board LED on when it receives "H" and off when it receives "L"
# from the computer. Type the letters in the REPL terminal (PyCharm's REPL
# or mpremote) while the script runs.
#
# sys.stdin.read(1) waits for the next character, so the loop pauses until
# one arrives.

import sys  # sys.stdin: characters typed in the terminal

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

mcu.led.off()  # start with the LED off
print("Type H to turn the LED on, L to turn it off.")

while True:  # repeats until you press Ctrl-C (or Stop in your editor)
    char = sys.stdin.read(1)  # wait for one character from the terminal
    if char == "H":
        mcu.led.on()
    elif char == "L":
        mcu.led.off()
    # Any other character is ignored.
