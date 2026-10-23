# Changelog

## 0.1.0-rc.1 (unreleased)

First version.

- `phyduino.py`: one-file library for the Phyduino Pico (RP2040) on the standard Raspberry Pi Pico MicroPython firmware, or built into the Phyduino Pico firmware.
  - `PINS` map and `pin()` / `gpio()` using the board's pin names (D0-D13, D18, D19, A0-A5, SDA, SCL, LED).
  - `pwm()` on the header pins and the LED, refusing pins that share a PWM output.
  - `led` for the on-board LED (GPIO5).
  - `analog_read()`, `analog_millivolts()`, `analog_volts()`, `analog_averaging()`, `analog_differential_millivolts()` and `analog_full_scale_millivolts()`, the same for A0-A5; A3-A5 use the on-board MAX11635, also available directly with `external_adc()`.
  - `vbus_volts()` and `cpu_temperature()`.
  - `usb_pd()`: STUSB4500 USB-PD profiles, contract and renegotiation (working registers only, 10 W limit).
  - `i2c()`, `spi()` and `uart()` on the header pins.
- `boards/PHYDUINO_PICO/`: MicroPython board definition (16 MB flash, board pin names, `phyduino.py` frozen in) and `tools/build_firmware.sh` to build it against MicroPython v1.29.0. Each GitHub release has the firmware UF2 and its SHA-256 attached.
- 25 examples in Arduino-style category folders (`01_basics/`, `02_digital/`, `03_analog/`, `04_communication/`) named after the Arduino IDE examples, plus `phyduino_pico/` for board features. Each is a `main.py` in its own folder (e.g. `01_basics/blink/main.py`), so it can be copied to the board and run at start-up, with `setup()` and `loop()`; host tests with a fake `machine` module.
- Documentation site (`docs/`) with a Doxygen API reference generated from the docstrings, published to GitHub Pages.
