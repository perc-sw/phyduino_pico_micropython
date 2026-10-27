# Plays a pitch on a piezo buzzer on D8 that follows the voltage on A0, from
# 120 Hz at 0 V to 1500 Hz at 3.3 V.
#
# Connect a piezo buzzer between D8 and GND, and a potentiometer wiper (ends
# on GND and 3.3 V) or a light sensor divider to A0.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUZZER_PIN = 8  # the buzzer is on D8
LOW_HZ = 120  # pitch at 0 V
HIGH_HZ = 1500  # pitch at 3.3 V


def setup():
    pass  # tone() sets the pin up the first time it is called


def loop():
    reading = analogRead(A0)  # 0 (0 V) to 1023 (3.3 V)
    pitch = map(reading, 0, 1023, LOW_HZ, HIGH_HZ)  # rescale 0-1023 to LOW_HZ-HIGH_HZ
    print(reading, pitch)
    tone(BUZZER_PIN, pitch)  # play that pitch until the next tone()
    delay(10)  # a short pause between readings


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
