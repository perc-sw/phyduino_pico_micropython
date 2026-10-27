# Fades the on-board LED up and down with PWM, about once every three seconds.
#
# analogWrite() takes 0 (off) to 255 (fully on); the brightness goes up in 51
# steps of 5, 30 ms apart, then back down.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

STEP = 5  # how much the brightness changes each time: 255 / 51

brightness = 0  # current brightness: 0 = off, 255 = fully on
fade_amount = STEP  # added to brightness each pass: positive brightens, negative dims


def setup():
    pass  # analogWrite() sets the pin up the first time it is called


def loop():
    global brightness, fade_amount  # loop() changes both, so it needs the ones above
    analogWrite(LED_BUILTIN, brightness)  # the fraction of the time the LED is on, out of 255
    brightness += fade_amount  # one step brighter (or dimmer) for next time
    if brightness <= 0 or brightness >= 255:
        fade_amount = -fade_amount  # at either end, turn round and go the other way
    delay(30)  # 30 ms per step, so the fade is smooth


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
