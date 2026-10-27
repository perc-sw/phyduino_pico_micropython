# Reads a potentiometer on A0, sets the on-board LED's brightness from it with
# PWM, and prints both numbers.
#
# Connect a potentiometer wiper to A0, with its ends on GND and 3.3 V.

import time  # sleep_ms() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

led = mcu.pwm("LED")  # Puts the LED's pin into PWM mode and saves the control variable to the 'led' variable.

while True:  # repeats until you press Ctrl-C (or Stop in your editor)
    sensor = mcu.analog_read("A0")  # 0 (0 V) to 4095 (3.3 V)
    output = sensor * 65535 // 4095  # scale to 0-65535 for duty_u16()
    led.duty_u16(output)  # brighter as the voltage rises
    print("sensor =", sensor, "  output =", output)
    time.sleep_ms(2)  # a short pause between readings
