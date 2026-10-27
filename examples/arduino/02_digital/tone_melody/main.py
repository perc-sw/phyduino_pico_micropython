# Plays a short tune on a piezo buzzer on D8, then waits two seconds and
# plays it again.
#
# Connect a piezo buzzer between D8 and GND (or a small speaker in series with
# a 100 Ohm resistor). tone() returns straight away, so delay() waits while
# the note plays.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUZZER_PIN = 8  # the buzzer is on D8

# Note frequencies in Hz; 0 is a rest.
NOTE_G3 = 196
NOTE_A3 = 220
NOTE_B3 = 247
NOTE_C4 = 262

MELODY = (NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4)
# Note lengths: 4 = quarter note, 8 = eighth note.
DURATIONS = (4, 8, 8, 4, 4, 4, 4, 4)


def setup():
    pass  # tone() sets the pin up the first time it is called


def loop():
    # zip() pairs each note with its length: (NOTE_C4, 4), (NOTE_G3, 8), ...
    for note, duration in zip(MELODY, DURATIONS):
        length_ms = 1000 // duration  # a quarter note is 1000 / 4 = 250 ms
        tone(BUZZER_PIN, note, length_ms)  # play the note (0 is a rest) for length_ms
        delay(length_ms * 13 // 10)  # wait for the note plus a 30 % gap, so the notes sound separate
        noTone(BUZZER_PIN)  # make sure the note has stopped
    delay(2000)  # wait two seconds before playing it again


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
