# API reference

A one-file MicroPython library for the University of Toronto Department of
Physics Phyduino Pico. Set-up steps are on the [home page](../index.html).

It is built into the Phyduino Pico firmware, so your own `main.py` can use it
straight away:

```{.py}
import phyduino as mcu

mcu.led.on()
print(mcu.analog_volts("A3"))
button = mcu.pin("D2", "in", pull="up")
```

Everything else in MicroPython (`time`, `machine.PWM`, ...) works as
described in the [MicroPython documentation](https://docs.micropython.org/en/latest/rp2/quickref.html);
use gpio() to find the RP2040 GPIO behind a pin name.

## Functions

| Topic | Use |
|---|---|
| @ref pins | `PINS`, pin(), gpio(), pwm() |
| @ref led | `led`: Led.on(), Led.off(), Led.toggle(), Led.value() |
| @ref analog | analog_read(), analog_millivolts(), analog_volts(), analog_averaging(), analog_differential_millivolts(), analog_full_scale_millivolts(), `ADC_FULL_SCALE_MILLIVOLTS`, `EXT_ADC_FULL_SCALE_MILLIVOLTS` |
| @ref power | vbus_volts(), cpu_temperature(), usb_pd(): STUSB4500.request(), STUSB4500.set_profiles(), STUSB4500.profiles(), STUSB4500.contract(), STUSB4500.contract_position(), STUSB4500.renegotiate() |
| @ref buses | i2c(), spi(), uart() |
| @ref arduino | arduino.py, optional: pinMode(), digitalWrite(), digitalRead(), analogRead(), analogReadResolution(), analogWrite(), analogWriteResolution(), analogWriteFreq(), tone(), noTone(), delay(), delayMicroseconds(), millis(), micros(), map(), constrain(), `HIGH`, `LOW`, `INPUT`, `OUTPUT`, `INPUT_PULLUP`, `INPUT_PULLDOWN`, `LED_BUILTIN`, `A0`-`A5` |
| @ref ext_adc | external_adc(): MAX11635.read(), MAX11635.scan(), MAX11635.read_differential(), MAX11635.set_averaging(), MAX11635.averaging |

Errors raise `ValueError` (a wrong pin name or setting) or `OSError` (an
on-board chip did not respond), with a message saying what to do.

## Examples

The @ref example_scripts page lets you choose between the two sets of example
scripts in `examples/`, which have the same examples:
@ref examples_arduino (`examples/arduino/`, setup() and loop()) and
@ref examples_phyduino (`examples/phyduino/`, plain MicroPython).
