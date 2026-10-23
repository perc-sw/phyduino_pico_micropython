# Hardware checklist

Run on a Phyduino Pico (Rev-E) with the standard RPI_PICO MicroPython firmware, after
`mpremote cp phyduino.py :`. Record the firmware version, board serial and results.

| # | Check | How | Expected | Result |
|---|---|---|---|---|
| 1 | LED | `mpremote run examples/01_basics/blink.py` | Green user LED (D8) blinks once a second | |
| 2 | Digital out | `mcu.pin("D7", "out", value=1)`, measure D7 | 3.3 V; `value=0` gives 0 V | |
| 3 | Digital in | `mcu.pin("D2", "in", pull="up").value()` with D2 open, then to GND | 1, then 0 | |
| 4 | A0 | Bench supply on A0 at 0 V, 1.000 V, 3.3 V; `mcu.analog_millivolts("A0")` | Within ±30 mV | |
| 5 | A3 | Bench supply on A3 at 0 V, 1.000 V, 2.048 V; `mcu.analog_millivolts("A3")` | Within ±5 mV; 2.048 V reads 4095 | |
| 6 | A4, A5 | As 5, on A4 and A5 | Same as A3 | |
| 7 | Averaging | `mpremote run examples/phyduino_pico/analog_averaging.py` | Spread shrinks as averaging rises | |
| 8 | Differential | A3 = 1.000 V, A4 = 0.900 V; `mcu.analog_differential_millivolts("A3", "A4")` | 100 ± 2 mV; swapped gives -100 | |
| 9 | VBUS, plain USB | `mcu.vbus_volts()` from a computer port | 4.75-5.25 V | |
| 10 | CPU temperature | `mcu.cpu_temperature()` | Room temperature, ±5 °C | |
| 11 | USB-PD | `examples/phyduino_pico/usb_pd_power.py` as `main.py`, USB-PD charger, UART0 to a USB-serial adapter; MAX_VOLTS 9 then 20 | Contract offer > 0; VBUS ≈ 9 V with POK2 on, then ≈ 20 V with POK3 on | |
| 12 | I2C | Sensor module with pull-ups on SDA/SCL; `mpremote run examples/04_communication/i2c_scanner.py` | Module's address listed | |
| 13 | UART | D1 jumpered to D0; `mpremote run examples/04_communication/uart_loopback.py` | Each message received unchanged | |
| 14 | SPI | `mcu.spi()` with D11 jumpered to D12; `bus.write_readinto(b"\x5a", buf)` | `buf` is `b"\x5a"` | |
| 15 | Errors | `mcu.pin("A3")`, `mcu.pin("D14")`, `mcu.pin("D77")` | Clear `ValueError` messages | |
| 16 | PWM | `mcu.pwm("D3", freq=1000, duty_u16=16384)`, scope on D3; then `mcu.pwm("LED").duty_u16(4096)` | 1 kHz, 25 % high; LED dim | |
| 17 | PWM sharing | `mcu.pwm("D1")`, then `mcu.pwm("D8")` | `ValueError` naming D1 | |
