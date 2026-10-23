# Plays a pitch on a piezo buzzer on D8 that follows the voltage on A0, from
# 120 Hz at 0 V to 1500 Hz at 3.3 V.
#
# Connect a piezo buzzer between D8 and GND, and a potentiometer wiper (ends
# on GND and 3.3 V) or a light sensor divider to A0.

import time  # sleep_ms() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

LOW_HZ = 120  # pitch at 0 V
HIGH_HZ = 1500  # pitch at 3.3 V

buzzer = None  # the buzzer's PWM output; setup() fills this in


def setup():
    global buzzer  # change the buzzer variable above, not a new one inside setup()
    buzzer = mcu.pwm("D8", duty_u16=32768)  # Puts D8 into PWM mode at half duty and saves the control variable to the 'buzzer' variable.


def loop():
    reading = mcu.analog_read("A0")  # 0 (0 V) to 4095 (3.3 V)
    # Scale 0-4095 to LOW_HZ-HIGH_HZ, like Arduino's map(). // divides to a whole number.
    pitch = LOW_HZ + reading * (HIGH_HZ - LOW_HZ) // 4095
    print(reading, pitch)
    buzzer.freq(pitch)  # change the pitch
    time.sleep_ms(10)  # a short pause between readings


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
