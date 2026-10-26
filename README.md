# Phyduino Pico MicroPython Library

[![CI](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/ci.yml/badge.svg)](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/ci.yml)
[![Docs](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/docs.yml/badge.svg)](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/docs.yml)
![Licence](https://img.shields.io/badge/licence-GPL--3.0-blue)

A one-file MicroPython library for the [Phyduino Pico](https://github.com/perc-sw/phyduino_pico)
used in the University of Toronto, Department of Physics,
"[Introduction to Electronics](https://plrs.physics.utoronto.ca/course-listing/)" course.

### Documentation: <https://perc-sw.github.io/phyduino_pico_micropython/>

It is built into the Phyduino Pico MicroPython firmware (on this repository's Releases page) and
adds what MicroPython doesn't know about this board:

- The pin names printed on the board (`"D7"`, `"A3"`, ...) instead of RP2040 GPIO numbers.
- The on-board LED.
- The external ADC interface for the on-board MAX11635 ADC (`"A3"` to `"A5"`).
- The USB-C supply voltage (VBUS) and the USB-PD controller.

### Example script

```python
import phyduino as mcu

mcu.led.on()
print(mcu.analog_volts("A3"))          # 0-2.048 V, on-board MAX11635
button = mcu.pin("D2", "in", pull="up")
print(button.value())
```

## Set up

The Phyduino Pico runs the `main.py` each time it starts. The firmware has the library,
`phyduino.py`, built in, so your `main.py` is the only file you put on the board.

### 1. Put the Phyduino Pico firmware on the board (once)

1. Download `phyduino_pico-<version>-micropython-<version>.uf2` from this repository's
   [Releases](https://github.com/perc-sw/phyduino_pico_micropython/releases) page.
2. Slide the boot switch (SW1) to the UF2 position and press RESET (SW2). The board appears as a
   drive named `RPI-RP2`.
3. Copy the UF2 onto that drive. Slide SW1 to the opposite position and press RESET.

***Installing MicroPython firmware erases the files on the board, back-up any files/code before downloading.***
(`mpremote cp :main.py .`).

The firmware uses the board's full 16 MB flash (about 15 MB for your files), knows the board's pin
names (`Pin("D7")`, `Pin("LED")`) and has `phyduino.py` built in. To check that it is the one on
the board:

```
mpremote exec "import os; print(os.uname().machine)"   # Phyduino Pico with RP2040
```

### 2. Run your code

A `phyduino.py` on the board takes priority over the built-in one, so delete any old copy
(`mpremote rm :phyduino.py`) to use the version in the firmware.

**PyCharm**

1. Install the **MicroPython Tools** plugin (Settings → Plugins → Marketplace).
2. Make a project with your `main.py`, and connect to the board from the plugin's tool window.
3. Run `main.py`, or upload it so it runs at start-up.

**Command line (or PyCharm's terminal)**

```
pip install mpremote
mpremote run main.py              # run your file without copying it
mpremote cp main.py :             # or copy it so it runs at start-up
```

## Pins

Use these names as strings, e.g. `mcu.pin("D7", "out")` or `mcu.analog_read("A0")`. Names are not
case-sensitive. `mcu.PINS` holds the whole map.

| Name | RP2040 | Notes |
|---|---|---|
| D0, D1 | GPIO1, GPIO0 | UART0 RX, TX: `mcu.uart(0)` |
| D2, D3 | GPIO6, GPIO7 | |
| D4, D5 | GPIO8, GPIO9 | UART1 TX, RX: `mcu.uart(1)` |
| D6, D7 | GPIO10, GPIO15 | |
| D8, D9 | GPIO16, GPIO17 | |
| D10-D13 | GPIO13, 11, 12, 14 | SPI1 CS, MOSI, MISO, SCK: `mcu.spi()` |
| D18 / SDA, D19 / SCL | GPIO24, GPIO25 | I2C0: `mcu.i2c()`. No pull-ups on the board |
| LED | GPIO5 | Green user LED: `mcu.led` |
| A0-A2 | GPIO26-28 | RP2040 ADC, 0-3.3 V. Can also be used as digital pins |
| A3-A5 | MAX11635 AIN0-2 | On-board ADC, 0-2.048 V. Analogue only |

There are no D14-D17. Some pairs of pins share a PWM channel, so they can't run different PWM
signals at once: D1/D8, D0/D9, D4/D18, D5/D19, D6/A0, D11/A1, D12/A2. `pwm()` refuses the second
pin of a pair until you call `pin()` on the first.

## Reference

| Function | Does |
|---|---|
| `pin(name, mode="in", pull=None, value=None)` | A `machine.Pin`; mode `"in"`, `"out"` or `"open_drain"`, pull `None`, `"up"` or `"down"` |
| `gpio(name)` | RP2040 GPIO number for a pin name |
| `pwm(name, freq=1000, duty_u16=0)` | A `machine.PWM`; change it with `.freq(hz)` and `.duty_u16(0-65535)` |
| `led.on()`, `led.off()`, `led.toggle()`, `led.value()` | On-board LED |
| `analog_read(name)` | A0-A5 as a 12-bit code, 0-4095 |
| `analog_millivolts(name)`, `analog_volts(name)` | A0-A5 in mV or V |
| `analog_averaging(samples)` | Average 1, 4, 8, 16 or 32 readings for every analogue result |
| `analog_differential_millivolts(plus, minus)` | `plus` minus `minus`; A3-A4 is a true simultaneous reading |
| `analog_full_scale_millivolts(name)` | 3300 for A0-A2, 2048 for A3-A5 |
| `vbus_volts()` | USB-C supply voltage (also on the VIN pin) |
| `cpu_temperature()` | RP2040 temperature in °C (roughly ±2 °C) |
| `i2c(freq)`, `spi(baudrate)`, `uart(number, baudrate)` | Buses on the header pins |
| `usb_pd()` | The USB-PD controller: `.request(max_volts)`, `.set_profiles([(5, 2), (9, 1)])`, `.profiles()`, `.contract()`, `.contract_position()`, `.renegotiate()` |
| `external_adc()` | The MAX11635 itself: `.read(ch)`, `.scan()`, `.read_differential()`, `.set_averaging()` |

Errors say what went wrong, e.g. `pin("A3")` reminds you that A3 is analogue only.

### Arduino-style functions (optional)

The firmware also has `arduino.py` built in, for code that reads like an Arduino sketch:

```python
from arduino import *

pinMode(13, OUTPUT)              # D13
digitalWrite(13, HIGH)
print(analogRead(A0))            # 0-1023, as on an Arduino
analogWrite(3, 128)              # PWM on D3, 0-255
```

| Function | Does |
|---|---|
| `pinMode(pin, mode)` | `INPUT`, `OUTPUT`, `INPUT_PULLUP` or `INPUT_PULLDOWN` |
| `digitalWrite(pin, value)`, `digitalRead(pin)` | `HIGH` or `LOW` |
| `analogRead(pin)`, `analogReadResolution(bits)` | A0-A5 (or 0-5), 10 bits (0-1023) unless changed |
| `analogWrite(pin, value)`, `analogWriteResolution(bits)`, `analogWriteFreq(hz)` | PWM, 8 bits (0-255) at 1 kHz unless changed |
| `tone(pin, frequency, duration)`, `noTone(pin)` | A note on a piezo buzzer; returns straight away |
| `delay(ms)`, `delayMicroseconds(us)`, `millis()`, `micros()` | Waits and time since start-up; `millis()` and `micros()` don't wrap round |
| `map(value, fromLow, fromHigh, toLow, toHigh)`, `constrain(value, low, high)` | Rescale and limit a number |

Pins are numbers (`13` is D13) or names (`"D13"`, `LED_BUILTIN`, `A0`-`A5`). Use `print()` for
`Serial.print()`, and `mcu.i2c()`, `mcu.spi()` and `mcu.uart()` for Wire, SPI and Serial1.
`from arduino import *` replaces Python's `map()` with the Arduino one.

## Examples

The examples are in folders named after the Arduino IDE's example categories, with
board-specific ones in `phyduino_pico/`. Each example is a `main.py` in its own folder (like an
Arduino sketch folder), because MicroPython runs `main.py` each time the board starts. Each is laid
out like an Arduino sketch: `setup()` runs once, then `loop()` runs over and over; leave the
`main()` at the end of each file as it is. Each file's header comment says what to connect and what
it prints.

With the Phyduino Pico firmware on the board, either:

- run an example without saving it: run it from PyCharm, or
  `mpremote run examples/01_basics/blink/main.py`;
- or copy its `main.py` to the board so it runs every time the board starts:
  `mpremote cp examples/01_basics/blink/main.py :` then press RESET.

| Example | Shows |
|---|---|
| `01_basics/bare_minimum/` | The empty setup() and loop() to start a program from |
| `01_basics/blink/` | Blinking the on-board LED |
| `01_basics/analog_read_serial/` | All six analogue pins as 12-bit codes |
| `01_basics/digital_read_serial/` | Printing the state of a pushbutton |
| `01_basics/fade/` | Fading the on-board LED with PWM |
| `01_basics/read_analog_voltage/` | All six analogue pins in millivolts |
| `02_digital/blink_without_delay/` | Timing with time.ticks_ms() instead of time.sleep() |
| `02_digital/button/` | Lighting the LED while a pushbutton is pressed |
| `02_digital/debounce/` | Ignoring contact bounce so each press counts once |
| `02_digital/digital_input_pullup/` | A pushbutton with the pin's own pull-up resistor |
| `02_digital/state_change_detection/` | Counting presses by detecting the edge |
| `02_digital/tone_melody/` | Playing a tune on a piezo buzzer |
| `02_digital/tone_pitch_follower/` | A pitch that follows an analogue input |
| `03_analog/analog_in_out_serial/` | Setting LED brightness from a potentiometer |
| `03_analog/calibration/` | Learning a sensor's range at start-up |
| `03_analog/smoothing/` | A running average of the last 10 readings |
| `04_communication/ascii_table/` | Characters with their decimal, hex, octal and binary values |
| `04_communication/graph/` | Sending readings to a serial plotter |
| `04_communication/i2c_scanner/` | Finding I2C devices on SDA/SCL |
| `04_communication/physical_pixel/` | Switching the LED from the computer |
| `04_communication/uart_loopback/` | UART0 with D1 jumpered to D0 |
| `phyduino_pico/analog_averaging/` | How averaging steadies a reading |
| `phyduino_pico/analog_differential/` | Voltage between two pins (A3-A4 true differential, A0-A1 computed) |
| `phyduino_pico/vbus_monitor/` | USB-C supply voltage and CPU temperature |
| `phyduino_pico/usb_pd_power/` | Asking a USB-PD charger for 9-20 V (output on UART0, since the charger takes the USB port) |

## Building the firmware

The Phyduino Pico firmware is built from `boards/PHYDUINO_PICO/` (a MicroPython board definition)
against a pinned MicroPython release, with `phyduino.py` built in:

```
tools/build_firmware.sh            # writes dist/phyduino_pico-<version>-micropython-<version>.uf2
tools/build_firmware.sh clean      # the same, after removing the previous build
```

It runs on Linux, or in WSL (Ubuntu) on Windows, and needs git, make, cmake, python3 and the Arm GNU
toolchain:

```
sudo apt install git make cmake python3 gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential
```

The first build downloads MicroPython and the parts it needs (pico-sdk, TinyUSB, ...) into `build/`
and takes several minutes; later builds only recompile what changed. Each release on GitHub has a
UF2 built the same way.

## Licence

GPL-3.0. See [LICENSE](LICENSE).
