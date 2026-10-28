# Counts presses of a pushbutton on D2 and lights the on-board LED at the
# start and on every fourth press. It acts on the change from released to pressed (an edge),
# not on the button being held down.
#
# Connect a pushbutton between D2 and 3.3 V; the pull-down holds D2 at 0
# while the button is open.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

BUTTON_PIN = 2  # the pushbutton is on D2

presses = 0  # how many times the button has been pressed
last_state = LOW  # the reading on the previous pass


def setup():
    pinMode(BUTTON_PIN, INPUT_PULLDOWN)  # D2 as an input, held LOW until pressed
    pinMode(LED_BUILTIN, OUTPUT)  # the LED's pin as an output


def loop():
    global presses, last_state  # loop() changes both, so it needs the ones above
    state = digitalRead(BUTTON_PIN)  # HIGH while pressed, LOW when not
    if state != last_state:  # it has changed since the last pass: an edge
        if state == HIGH:  # released to pressed
            presses += 1
            print("on")
            print("number of button pushes:", presses)
        else:  # pressed to released
            print("off")
        delay(50)  # let the contacts settle (bounce) before reading again
    last_state = state  # compare against this next time
    if presses % 4 == 0:  # % is the remainder: true at 0, 4, 8, ... presses
        digitalWrite(LED_BUILTIN, HIGH)  # LED on
    else:
        digitalWrite(LED_BUILTIN, LOW)  # LED off


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
