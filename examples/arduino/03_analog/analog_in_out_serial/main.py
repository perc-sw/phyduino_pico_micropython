# Reads a potentiometer on A0, sets the on-board LED's brightness from it with
# PWM, and prints both numbers.
#
# Connect a potentiometer wiper to A0, with its ends on GND and 3.3 V.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    pass  # analogRead() and analogWrite() need no set-up


def loop():
    sensor = analogRead(A0)  # 0 (0 V) to 1023 (3.3 V)
    output = map(sensor, 0, 1023, 0, 255)  # rescale to 0-255 for analogWrite()
    analogWrite(LED_BUILTIN, output)  # brighter as the voltage rises
    print("sensor =", sensor, "  output =", output)
    delay(2)  # a short pause between readings


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
