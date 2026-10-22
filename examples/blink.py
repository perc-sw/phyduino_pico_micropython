# Blinks the on-board green LED once a second.

import time

import phyduino as pd

while True:
    pd.led.toggle()
    time.sleep(0.5)
