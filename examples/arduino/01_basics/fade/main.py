# Fades the on-board LED up and down with PWM, about once every three seconds.
#
# The duty cycle goes from 0 (off) to 65535 (fully on) in 51 steps, 30 ms
# apart, then back down.

import time  # sleep() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

STEP = 1285  # how much the brightness changes each time: 65535 / 51

led = None  # the LED's PWM output; setup() fills this in
brightness = 0  # current duty cycle: 0 = off, 65535 = fully on
fade_amount = STEP  # added to brightness each pass: positive brightens, negative dims


def setup():
    global led
    # change the LED variable above, not a new one inside setup()
    led = mcu.pwm("LED") # Puts the LED's pin into PWM mode and saves the control variable to the 'led' variable.


def loop():
    global brightness, fade_amount  # loop() changes both, so it needs the ones above
    led.duty_u16(brightness)  # the fraction of the time the LED is on, out of 65535
    brightness += fade_amount  # one step brighter (or dimmer) for next time
    if brightness <= 0 or brightness >= 65535:
        fade_amount = -fade_amount  # at either end, turn round and go the other way
    time.sleep(0.03)  # 30 ms per step, so the fade is smooth


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
