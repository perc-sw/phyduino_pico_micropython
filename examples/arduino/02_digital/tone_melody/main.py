# Plays a short tune on a piezo buzzer on D8, then waits two seconds and
# plays it again.
#
# Connect a piezo buzzer between D8 and GND (or a small speaker in series with
# a 100 Ohm resistor). MicroPython has no tone(): a PWM output at 50 % duty
# makes the note, and a duty of 0 is silence.

import time  # sleep() and sleep_ms() for pauses

import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

# Note frequencies in Hz; 0 is a rest.
NOTE_G3 = 196
NOTE_A3 = 220
NOTE_B3 = 247
NOTE_C4 = 262

MELODY = (NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4)
# Note lengths: 4 = quarter note, 8 = eighth note.
DURATIONS = (4, 8, 8, 4, 4, 4, 4, 4)

buzzer = None  # the buzzer's PWM output; setup() fills this in


def tone(frequency, duration_ms):
    """Plays one note (or a rest, if frequency is 0) for duration_ms."""
    if frequency:  # 0 counts as false, so a rest skips this
        buzzer.freq(frequency)  # the pitch: how many times a second the pin switches
        buzzer.duty_u16(32768)  # half of 65535: high half the time, which makes a tone
    time.sleep_ms(duration_ms)  # let the note sound
    buzzer.duty_u16(0)  # always low: silence


def setup():
    global buzzer  # change the buzzer variable above, not a new one inside setup()
    buzzer = mcu.pwm("D8")  # Puts D8 into PWM mode and saves the control variable to the 'buzzer' variable.


def loop():
    # zip() pairs each note with its length: (NOTE_C4, 4), (NOTE_G3, 8), ...
    for note, duration in zip(MELODY, DURATIONS):
        length_ms = 1000 // duration  # a quarter note is 1000 / 4 = 250 ms
        tone(note, length_ms)
        time.sleep_ms(length_ms * 3 // 10)  # a gap of 30 % so the notes sound separate
    time.sleep(2)  # wait two seconds before playing it again


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
