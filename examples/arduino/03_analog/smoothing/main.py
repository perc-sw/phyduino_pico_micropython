# Prints a running average of the last 10 readings of A0, which steadies a
# noisy signal. Each new reading replaces the oldest one.
#
# Connect a potentiometer wiper or sensor to A0 (0-3.3 V). For averaging done
# by the board itself, see phyduino_pico/analog_averaging/.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

NUM_READINGS = 10  # how many readings to average; more is smoother but slower to follow

readings = [0] * NUM_READINGS  # the last 10 readings, all 0 to begin with
index = 0  # where the next reading goes in the list
total = 0  # the sum of the readings in the list


def setup():
    pass  # analogue pins need no set-up


def loop():
    global index, total  # loop() changes both, so it needs the ones above
    total -= readings[index]  # take the oldest reading out of the sum
    readings[index] = analogRead(A0)  # replace it with a new one, 0-1023
    total += readings[index]  # and add that to the sum
    index = (index + 1) % NUM_READINGS  # move along; % wraps back to 0 after the end
    print(total // NUM_READINGS)  # the average
    delay(1)  # a short pause between readings


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
