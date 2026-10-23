# Phyduino Pico MicroPython Library

[![CI](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/ci.yml/badge.svg)](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/ci.yml)
[![Docs](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/docs.yml/badge.svg)](https://github.com/perc-sw/phyduino_pico_micropython/actions/workflows/docs.yml)
![Licence](https://img.shields.io/badge/licence-GPL--3.0-blue)

A one-file MicroPython library for the [Phyduino Pico](https://github.com/perc-sw/phyduino_pico)
used in the University of Toronto, Department of Physics,
"[Introduction to Electronics](https://plrs.physics.utoronto.ca/course-listing/)" course.

Documentation: <https://perc-sw.github.io/phyduino_pico_micropython/>

It runs on the standard Raspberry Pi Pico (RP2040) MicroPython firmware and adds what that firmware
doesn't know about this board:

- the pin names printed on the board (`"D7"`, `"A3"`, ...) instead of RP2040 GPIO numbers;
- the on-board LED, which is on GPIO5 (MicroPython's own `Pin("LED")` is GPIO25, the D19 pin here);
- A3-A5, which are read by the on-board MAX11635 ADC rather than the RP2040;
- the USB-C supply voltage (VBUS) and the USB-PD controller.

```python
import phyduino as mcu

mcu.led.on()
print(mcu.analog_volts("A3"))          # 0-2.048 V, on-board MAX11635
button = mcu.pin("D2", "in", pull="up")
print(button.value())
```

## Set up

The board runs `main.py` each time it starts. It also needs the library, `phyduino.py`: either
built into the Phyduino Pico firmware, or copied onto the board next to your `main.py`.

### 1. Put MicroPython on the board (once)

Choose one firmware:

- **Phyduino Pico firmware (recommended).** Download
  `phyduino_pico-<version>-micropython-<version>.uf2` from this repository's
  [Releases](https://github.com/perc-sw/phyduino_pico_micropython/releases) page. It uses the board's full 16 MB flash (about 15 MB for your files),
  knows the board's pin names (`Pin("D7")`, `Pin("LED")`), and has `phyduino.py` built in, so there
  is nothing to copy in step 2.
- **Standard Raspberry Pi Pico firmware.** Download the latest **Raspberry Pi Pico** (RP2040) UF2
  from <https://micropython.org/download/RPI_PICO/>, then copy `phyduino.py` to the board in step 2.
  It only uses 2 MB of the flash (about 1.4 MB for files).

Then, for either one:

1. Slide the boot switch (SW1) to the boot position and press RESET (SW2). The board appears as a
   drive named `RPI-RP2`.
2. Copy the UF2 onto that drive. Slide SW1 back and press RESET.

Installing a firmware erases the files on the board, so copy off anything you want to keep first
(`mpremote cp :main.py .`).

### 2. Copy the library and run your code

On the Phyduino Pico firmware, skip copying `phyduino.py`: it is built in. A copy on the board
takes priority over the built-in one, so delete any old copy to use the built-in version.

**VS Code**

1. Install the [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go)
   extension. (Opening this repository in VS Code offers to install it.)
2. Make a folder for your project with `phyduino.py` and your `main.py` in it, and open the folder.
3. Run **MicroPico: Initialize MicroPico Project** from the Command Palette (Ctrl+Shift+P). This
   adds autocompletion for MicroPython's built-in modules.
4. With the board plugged in, right-click `phyduino.py` and choose **Upload file to Pico**.
5. Open `main.py` and click **Run** in the status bar, or upload it as well so it runs at start-up.

**PyCharm**

1. Install the **MicroPython Tools** plugin (Settings → Plugins → Marketplace).
2. Make a project with `phyduino.py` and your `main.py`, and connect to the board from the
   plugin's tool window.
3. Upload `phyduino.py` to the board, then run or upload `main.py`.

**Command line (either IDE's terminal)**

```
pip install mpremote
mpremote cp phyduino.py :         # copy the library to the board
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

## Examples

The examples are in folders named after the Arduino IDE's example categories, with
board-specific ones in `phyduino_pico/`. Each example is a `main.py` in its own folder (like an
Arduino sketch folder), because MicroPython runs `main.py` each time the board starts. Each is laid
out like an Arduino sketch: `setup()` runs once, then `loop()` runs over and over; leave the
`main()` at the end of each file as it is. Each file's header comment says what to connect and what
it prints.

Copy `phyduino.py` to the board first (not needed on the Phyduino Pico firmware, which has it
built in), then either:

- run an example without saving it: MicroPico's **Run**, or
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
