"""@package arduino
@brief Arduino-style functions for the Phyduino Pico, built on phyduino.py.

Built into the Phyduino Pico firmware next to phyduino.py. Optional: use it
when you want code that reads like an Arduino sketch.
@code
from arduino import *

pinMode(LED_BUILTIN, OUTPUT)
digitalWrite(LED_BUILTIN, HIGH)
print(analogRead(A0))
@endcode

Digital pins are numbers, as on an Arduino: 2 is D2, 13 is D13. The names
used by phyduino.py ("D2", "A0", "LED") work too. analogRead() also takes
0-5 for A0-A5.

The ranges are Arduino's: analogRead() gives 0-1023 and analogWrite() takes
0-255 until analogReadResolution() or analogWriteResolution() changes them.

`from arduino import *` replaces Python's map() with the Arduino one; use
`import arduino` if your code needs Python's map().

Licence: GPL-3.0.
"""

import time

from machine import Timer

import phyduino as _mcu

# --- Constants --------------------------------------------------------------------

## @brief Pin level: high (3.3 V).
# @ingroup arduino
HIGH = 1
## @brief Pin level: low (0 V).
# @ingroup arduino
LOW = 0

## @brief pinMode(): a digital input with no pull resistor.
# @ingroup arduino
INPUT = 0
## @brief pinMode(): a digital output.
# @ingroup arduino
OUTPUT = 1
## @brief pinMode(): a digital input pulled up to 3.3 V.
# @ingroup arduino
INPUT_PULLUP = 2
## @brief pinMode(): a digital input pulled down to 0 V.
# @ingroup arduino
INPUT_PULLDOWN = 3

## @brief The on-board green LED.
# @ingroup arduino
LED_BUILTIN = "LED"

## @brief Analogue pin A0 (RP2040 ADC, 0-3.3 V).
# @ingroup arduino
A0 = "A0"
## @brief Analogue pin A1 (RP2040 ADC, 0-3.3 V).
# @ingroup arduino
A1 = "A1"
## @brief Analogue pin A2 (RP2040 ADC, 0-3.3 V).
# @ingroup arduino
A2 = "A2"
## @brief Analogue pin A3 (MAX11635, 0-2.048 V). Analogue only.
# @ingroup arduino
A3 = "A3"
## @brief Analogue pin A4 (MAX11635, 0-2.048 V). Analogue only.
# @ingroup arduino
A4 = "A4"
## @brief Analogue pin A5 (MAX11635, 0-2.048 V). Analogue only.
# @ingroup arduino
A5 = "A5"

_MODES = {
    INPUT: ("in", None),
    OUTPUT: ("out", None),
    INPUT_PULLUP: ("in", "up"),
    INPUT_PULLDOWN: ("in", "down"),
}

_pins = {}      # pin name -> (mode, machine.Pin) set up by pinMode()
_pwms = {}      # pin name -> machine.PWM set up by analogWrite() or tone()
_tone_timer = None
_read_bits = 10
_write_bits = 8
_write_freq = 1000


def _key(pin, prefix="D"):
    if isinstance(pin, int):
        pin = prefix + str(pin)
    return _mcu._name(pin)


# --- Digital pins -----------------------------------------------------------------

def pinMode(pin, mode):
    """@brief Sets a pin up as an input or an output.

    @param pin  Pin number (2 is D2) or name ("D2", "A0", LED_BUILTIN).
    @param mode INPUT, OUTPUT, INPUT_PULLUP or INPUT_PULLDOWN.
    @exception ValueError Unknown pin or mode, or an analogue-only pin (A3-A5).
    @ingroup arduino
    """
    if mode not in _MODES:
        raise ValueError("mode must be INPUT, OUTPUT, INPUT_PULLUP or INPUT_PULLDOWN")
    key = _key(pin)
    direction, pull = _MODES[mode]
    _pins[key] = (mode, _mcu.pin(key, direction, pull=pull))
    _pwms.pop(key, None)  # pin() takes the pin off PWM


def digitalWrite(pin, value):
    """@brief Sets an output pin high or low.

    A pin that is not an output yet (or is on analogWrite()) becomes one.

    @param pin   Pin number (2 is D2) or name ("D2", "A0", LED_BUILTIN).
    @param value HIGH or LOW.
    @ingroup arduino
    """
    key = _key(pin)
    if key not in _pins or _pins[key][0] != OUTPUT:
        pinMode(key, OUTPUT)
    _pins[key][1].value(1 if value else 0)


def digitalRead(pin):
    """@brief Reads a pin's level.

    A pin that has not been set up with pinMode() becomes an INPUT.

    @param pin Pin number (2 is D2) or name ("D2", "A0").
    @return HIGH or LOW.
    @ingroup arduino
    """
    key = _key(pin)
    if key not in _pins:
        pinMode(key, INPUT)
    return _pins[key][1].value()


# --- Analogue pins ----------------------------------------------------------------

def analogReadResolution(bits):
    """@brief Sets the number of bits analogRead() returns.

    @param bits 1-16. 10 (0-1023) at start-up; 12 (0-4095) is the ADCs' own resolution.
    @exception ValueError bits is outside 1-16.
    @ingroup arduino
    """
    global _read_bits
    if not 1 <= bits <= 16:
        raise ValueError("bits must be 1-16")
    _read_bits = bits


def analogRead(pin):
    """@brief Reads an analogue pin.

    @param pin A0-A5, or 0-5 for A0-A5.
    @return 0-1023 at the default 10 bits. A0-A2: top = 3.3 V. A3-A5: top = 2.048 V.
    @exception ValueError Not an analogue pin.
    @exception OSError    The external ADC did not respond (A3-A5).
    @ingroup arduino
    """
    code = _mcu.analog_read(_key(pin, "A"))  # 12 bits
    if _read_bits <= 12:
        return code >> (12 - _read_bits)
    return code << (_read_bits - 12)


def analogWriteResolution(bits):
    """@brief Sets the range analogWrite() takes.

    @param bits 1-16. 8 (0-255) at start-up.
    @exception ValueError bits is outside 1-16.
    @ingroup arduino
    """
    global _write_bits
    if not 1 <= bits <= 16:
        raise ValueError("bits must be 1-16")
    _write_bits = bits


def analogWriteFreq(hz):
    """@brief Sets the PWM frequency for analogWrite() on pins set up after this.

    @param hz Frequency in Hz, 8 Hz and up. 1000 at start-up.
    @ingroup arduino
    """
    global _write_freq
    _write_freq = hz


def _pwm(key):
    if key not in _pwms:
        _pwms[key] = _mcu.pwm(key, freq=_write_freq)
        _pins.pop(key, None)  # no longer a digital pin
    return _pwms[key]


def analogWrite(pin, value):
    """@brief Puts a PWM signal on a pin: a fraction of the time high.

    Pairs of pins share a PWM output; see pwm() in phyduino.py.

    @param pin   Pin number (3 is D3) or name ("D3", "A0", LED_BUILTIN).
    @param value 0 (always low) to 255 (always high) at the default 8 bits;
                 values outside the range are clamped.
    @exception ValueError Unknown pin, an analogue-only pin (A3-A5), or the pin
                          shares its PWM output with one already in use.
    @ingroup arduino
    """
    top = (1 << _write_bits) - 1
    value = constrain(int(value), 0, top)
    _pwm(_key(pin)).duty_u16(value * 65535 // top)


# --- Tones ------------------------------------------------------------------------

def tone(pin, frequency, duration=None):
    """@brief Plays a square wave (a note) on a pin, for example for a piezo buzzer.

    Returns straight away; the note plays on while your code runs.

    @param pin       Pin number (8 is D8) or name ("D8").
    @param frequency Frequency in Hz, 8 Hz and up; 0 is silence.
    @param duration  Milliseconds to play for; None plays until noTone().
    @ingroup arduino
    """
    global _tone_timer
    if _tone_timer is not None:
        _tone_timer.deinit()  # a new note replaces the old one's stop time
        _tone_timer = None
    if not frequency:
        noTone(pin)
        return
    p = _pwm(_key(pin))
    p.freq(frequency)
    p.duty_u16(32768)
    if duration is not None:
        _tone_timer = Timer(mode=Timer.ONE_SHOT, period=int(duration),
                            callback=lambda t: p.duty_u16(0))


def noTone(pin):
    """@brief Stops a tone() on a pin.

    @param pin Pin number (8 is D8) or name ("D8").
    @ingroup arduino
    """
    key = _key(pin)
    if key in _pwms:
        _pwms[key].duty_u16(0)


# --- Time -------------------------------------------------------------------------

# MicroPython's ticks wrap round (ticks_ms every 12 days, ticks_us every 18
# minutes), so millis() and micros() add up the time between calls instead.
_last_ms = time.ticks_ms()
_millis = _last_ms
_last_us = time.ticks_us()
_micros = _millis * 1000  # ticks_us may have wrapped already; ticks_ms hasn't


def delay(ms):
    """@brief Waits a number of milliseconds.

    @param ms Milliseconds.
    @ingroup arduino
    """
    time.sleep_ms(int(ms))


def delayMicroseconds(us):
    """@brief Waits a number of microseconds.

    @param us Microseconds.
    @ingroup arduino
    """
    time.sleep_us(int(us))


def millis():
    """@brief Milliseconds since the board started.

    Never wraps round, as long as it is called at least every 6 days.

    @return Milliseconds.
    @ingroup arduino
    """
    global _last_ms, _millis
    now = time.ticks_ms()
    _millis += time.ticks_diff(now, _last_ms)
    _last_ms = now
    return _millis


def micros():
    """@brief Microseconds since the board started.

    Never wraps round, as long as it is called at least every 8 minutes.

    @return Microseconds.
    @ingroup arduino
    """
    global _last_us, _micros
    now = time.ticks_us()
    _micros += time.ticks_diff(now, _last_us)
    _last_us = now
    return _micros


# --- Maths ------------------------------------------------------------------------

def map(value, fromLow, fromHigh, toLow, toHigh):
    """@brief Rescales a number from one range to another.

    With whole numbers the result is a whole number, rounded towards zero as
    on an Arduino; with any float it is a float. Not clamped: use constrain().

    @param value    The number to rescale.
    @param fromLow  Bottom of the range value is in.
    @param fromHigh Top of the range value is in.
    @param toLow    Bottom of the new range.
    @param toHigh   Top of the new range.
    @return The rescaled number.

    @par Example
    @code
    analogWrite(3, map(analogRead(A0), 0, 1023, 0, 255))
    @endcode
    @ingroup arduino
    """
    top = (value - fromLow) * (toHigh - toLow)
    bottom = fromHigh - fromLow
    if all(isinstance(n, int) for n in (value, fromLow, fromHigh, toLow, toHigh)):
        quotient = abs(top) // abs(bottom)
        return (quotient if (top < 0) == (bottom < 0) else -quotient) + toLow
    return top / bottom + toLow


def constrain(value, low, high):
    """@brief Limits a number to a range.

    @param value The number.
    @param low   The smallest result.
    @param high  The largest result.
    @return low if value is below it, high if above it, otherwise value.
    @ingroup arduino
    """
    if value < low:
        return low
    if value > high:
        return high
    return value
