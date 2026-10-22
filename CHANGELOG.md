# Changelog

## 0.1.0-rc.1 (unreleased)

First version.

- `phyduino.py`: one-file library for the Phyduino Pico (RP2040) on the standard Raspberry Pi Pico MicroPython firmware.
  - `PINS` map and `pin()` / `gpio()` using the board's pin names (D0-D13, D18, D19, A0-A5, SDA, SCL, LED).
  - `led` for the on-board LED (GPIO5).
  - `analog_read()`, `analog_millivolts()`, `analog_volts()`, `analog_averaging()` and `analog_differential_millivolts()`, the same for A0-A5; A3-A5 use the on-board MAX11635.
  - `vbus_volts()` and `cpu_temperature()`.
  - `usb_pd()`: STUSB4500 USB-PD profiles, contract and renegotiation (working registers only, 10 W limit).
  - `i2c()`, `spi()` and `uart()` on the header pins.
- Examples, host tests with a fake `machine` module, and a hardware checklist.
- Documentation site (`docs/`) with a Doxygen API reference generated from the docstrings, published to GitHub Pages.
