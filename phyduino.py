"""@package phyduino
@brief Phyduino Pico board library for MicroPython.

Built into the Phyduino Pico MicroPython firmware, so your own main.py can use it:
@code
import phyduino as mcu

mcu.led.on()
print(mcu.analog_volts("A3"))
button = mcu.pin("D2", "in", pull="up")
@endcode

Pins use the names printed on the board: "D0"-"D13", "D18", "D19", "A0"-"A5",
plus "SDA", "SCL" and "LED". Names are not case-sensitive.

A0-A2 are read by the RP2040 (0-3.3 V). A3-A5 are read by the on-board
MAX11635 ADC (0-2.048 V) and are analog only. The same functions work on
all six analog inputs.

Licence: GPL-3.0.
"""

import time

from machine import ADC, I2C, PWM, Pin, SPI, UART, mem32
from micropython import const

## Library version, MAJOR.MINOR.PATCH.
__version__ = "0.1.0-rc.1"

# --- Pin map ----------------------------------------------------------------------

# Markers for A3-A5: these pins have no RP2040 GPIO. They are MAX11635 inputs 0-2.
_EXT = const(0x100)

## @brief Every pin name on the board and the RP2040 GPIO it connects to.
#
# A3-A5 have no RP2040 GPIO; their values are markers for the MAX11635 inputs
# and are not GPIO numbers. Use gpio() to look a name up.
# @ingroup pins
PINS = {
    "D0": 1,  # UART0 RX
    "D1": 0,  # UART0 TX
    "D2": 6,
    "D3": 7,
    "D4": 8,  # UART1 TX
    "D5": 9,  # UART1 RX
    "D6": 10,
    "D7": 15,
    "D8": 16,
    "D9": 17,
    "D10": 13,  # SPI1 CS
    "D11": 11,  # SPI1 MOSI
    "D12": 12,  # SPI1 MISO
    "D13": 14,  # SPI1 SCK
    "D18": 24,  # I2C0 SDA
    "D19": 25,  # I2C0 SCL
    "SDA": 24,
    "SCL": 25,
    "LED": 5,
    "A0": 26,  # RP2040 ADC0
    "A1": 27,  # RP2040 ADC1
    "A2": 28,  # RP2040 ADC2
    "A3": _EXT | 0,  # MAX11635 AIN0
    "A4": _EXT | 1,  # MAX11635 AIN1
    "A5": _EXT | 2,  # MAX11635 AIN2
}

_ANALOG = ("A0", "A1", "A2", "A3", "A4", "A5")
_D19_GPIO = const(25)  # schematic: GPIO25 must use 12 mA drive
# MicroPython's rp2 Pin has no drive-strength option, so set the pad register
# directly: RP2040 PADS_BANK0, GPIOn at 0x4001C004 + 4n, DRIVE in bits 5:4.
_PADS_BANK0_GPIO0 = const(0x4001C004)
_PAD_DRIVE_MASK = const(0x30)
_PAD_DRIVE_12MA = const(0x30)


def _set_d19_drive_12ma():
    reg = _PADS_BANK0_GPIO0 + 4 * _D19_GPIO
    mem32[reg] = (mem32[reg] & ~_PAD_DRIVE_MASK) | _PAD_DRIVE_12MA


## @brief Maximum input voltage of A0-A2 (RP2040 ADC) in millivolts.
# @ingroup analog
ADC_FULL_SCALE_MILLIVOLTS = 3300
## @brief Maximum input voltage A3-A5 (MAX11635, LM4040 reference on AREF) in millivolts.
# @ingroup analog
EXT_ADC_FULL_SCALE_MILLIVOLTS = 2048


def _name(name):
    if not isinstance(name, str):
        raise TypeError("pin names are strings, e.g. 'D7' or 'A3'")
    key = name.strip().upper()
    if key in PINS:
        return key
    if key in ("D14", "D15", "D16", "D17"):
        raise ValueError(
            "the Phyduino Pico has no pin " + key + "; digital pins are D0-D13, D18 and D19")
    raise ValueError(
        "unknown pin " + repr(name) + "; use one of: " + ", ".join(sorted(PINS)))


def gpio(name):
    """@brief Gets the GPIO number from the board header name.

    For MicroPython's own machine module, which numbers pins by GPIO. Two
    names can share a GPIO: "D18" and "SDA" are both GPIO24.

    @param name Pin name, e.g. "D7" (not case-sensitive).
    @return GPIO number, e.g. gpio("D7") is 15.
    @exception ValueError The name is unknown, or is A3-A5 (no RP2040 GPIO).
    @exception TypeError  The name is not a string.
    @ingroup pins
    """
    key = _name(name)
    if PINS[key] & _EXT:
        raise ValueError(key + " is on the external ADC and has no RP2040 GPIO")
    return PINS[key]


_MODES = {"in": Pin.IN, "out": Pin.OUT, "open_drain": Pin.OPEN_DRAIN}
_PULLS = {None: None, "up": Pin.PULL_UP, "down": Pin.PULL_DOWN}


def pin(name, mode="in", pull=None, value=None):
    """@brief Configures the GPIO pin from board header name.

    Sets the pin configuration and returns GPIO interface. The following functions can be used
    to set the state of the pin or read.

     - .value(1) : Sets pin state HIGH
     - .value(0) : Sets pin state LOW
     - .on() : Sets pin state HIGH
     - .off() : Sets pin state LOW
     - value() : Read the state of the pin.

    A0-A2 can be configured to work as digital pins as well.

    In addition to writing & reading the pin states with the returned Pin class, the GPIO
    can be configured INPUT/OUTPUT or OPEN DRAIN. Internal pull-ups and pull-down resistors
    are also available. If function parameters listed below for GPIO configuration are left
    output of the function all the default setting is : DIRECTION := INPUT, PULL := NONE, and VALUE = 0.

    If the pin was on PWM, calling pin() reverts the GPIO pin back to GPIO control not the peripheral it
    was attached to.

    @note LED GPIO pin is set to 12 mA drive for proper LED illumination by default.

    Refer to MicroPython documentation for more information about the returned object :
    https://docs.micropython.org/en/latest/library/machine.Pin.html

    @param name  Pin name: "D0"-"D13", "D18", "D19", "A0"-"A2", "SDA", "SCL" or "LED".
    @param mode  "in", "out" or "open_drain" (drives low for 0, lets go for 1).
    @param pull  None, "up" or "down": the RP2040's built-in pull resistor.
    @param value Starting level for outputs, 0 or 1; None leaves it unchanged.

    @return A machine.Pin.

    @exception ValueError Unknown name, mode or pull, or an analog-only pin (A3-A5).
    @exception TypeError  The name is not a string.

    @par Example
    @code
    led = mcu.pin("D7", "out")
    led.value(1)
    button = mcu.pin("D2", "in", pull="up")
    @endcode
    @ingroup pins
    """
    key = _name(name)

    if PINS[key] & _EXT:
        raise ValueError(
            key + " is an analogue-only pin; use analog_read('" + key + "') instead")

    if mode not in _MODES:
        raise ValueError("mode must be 'in', 'out' or 'open_drain'")

    if pull not in _PULLS:
        raise ValueError("pull must be None, 'up' or 'down'")

    number = PINS[key]
    kwargs = {}

    if value is not None:
        kwargs["value"] = value

    p = Pin(number, _MODES[mode], _PULLS[pull], **kwargs)

    if number == _D19_GPIO:
        _set_d19_drive_12ma()

    output = _pwm_output(number)

    if output in _pwm_users and PINS[_pwm_users[output]] == number:
        del _pwm_users[output]  # this pin is no longer a PWM output

    return p


# --- PWM --------------------------------------------------------------------------

# RP2040 PWM: GPIOn is output A if n is an even number or B if n is an odd number of slice; (n >> 1) & 7.
# Two pins on the same output give the same signal; the two outputs of a slice
# share one frequency.
_pwm_users = {}  # (slice, output) -> name of the pin last given to pwm()


def _pwm_output(number):
    return (number >> 1) & 7, number & 1


def pwm(name, freq=1000, duty_u16=0):
    """@brief Configures GPIO pin for PWM output.

    PWM generators on the RP2040 are set up in pairs, a PWM sliced with outputs A and B. PWM
    frequency can set on a per-slice basis. If a 2 PWM pins share the same PWM slice the PWM frequency
    of both pins will be the same. However, the user can change the duty cycle of each pair
    separately. PWM that share PWM slices are as follows:

        - D1/D8
        - D0/D9
        - D4/D18
        - D5/D19
        - D6/A0
        - D11/A1
        - D12/A2

    Calling pin() on a pin frees its output.

    @note Set the duty to 0 before your program ends if that matters (a buzzer or a motor).

    Refer to MicroPython documentation for more information about the returned object :
    https://docs.micropython.org/en/latest/library/machine.PWM.html

    @param name     Pin name: "D0"-"D13", "D18", "D19", "A0"-"A2", "SDA", "SCL" or "LED".
    @param freq     Frequency in Hz, 8 Hz and up.
    @param duty_u16 Starting duty cycle, 0 (always low) to 65535 (always high);
                    32768 is high half the time.
    @return A machine.PWM; change it with .freq(hz) and .duty_u16(duty).
    @exception ValueError Unknown name, an analogue-only pin (A3-A5), or the
                          pin shares its PWM output with one already in use.

    @par Example
    @code
    glow = mcu.pwm("LED")
    glow.duty_u16(32768)  # half brightness
    buzzer = mcu.pwm("D3", freq=440, duty_u16=32768)
    @endcode
    @ingroup pins
    """
    key = _name(name)
    number = gpio(key)
    output = _pwm_output(number)
    other = _pwm_users.get(output)
    if other is not None and PINS[other] != number:
        raise ValueError(
            key + " and " + other + " share a PWM output and " + other
            + " is already PWM; use another pin, or call pin('" + other + "') to free it")
    p = PWM(pin(key, "out"))
    p.freq(freq)
    p.duty_u16(duty_u16)
    _pwm_users[output] = key
    return p


# --- On-board LED -----------------------------------------------------------------

class Led:
    """@brief Gives control of the built-in LED (D8) on GPIO5.

    Use the class object to control the built-in LED (D8) on GPIO5. When call it
    sets up the GPIO5 as an OUTPUT and set the drive strength to 12mA. The class
    will allow you to turn the LED on/off/toggle.

    @note This pin can also be set up as a PWM pin. If you wish to use GPIO again
    you must call Led() again.

    @code
    mcu.led.on()
    mcu.led.toggle()
    @endcode
    @ingroup led
    """

    def __init__(self):
        self._pin = None

    def _get(self):
        if self._pin is None:
            self._pin = Pin(PINS["LED"], Pin.OUT, value=0)
        return self._pin

    def on(self):
        """@brief Turns the LED on."""
        self._get().value(1)

    def off(self):
        """@brief Turns the LED off."""
        self._get().value(0)

    def toggle(self):
        """@brief Turns the LED on if it is off, and off if it is on."""
        p = self._get()
        p.value(not p.value())

    def value(self, level=None):
        """@brief Reads or sets the LED.

        @param level None to read; 1 (on) or 0 (off) to set.
        @return 1 (on) or 0 (off) when reading; None when setting.
        """
        if level is None:
            return self._get().value()
        self._get().value(level)


## @brief The on-board LED: a Led object.
# @ingroup led
led = Led()

# --- MAX11635 external ADC (A3-A5, VBUS) ------------------------------------------

# Register select bits (top bits of each command byte).
_REG_CONVERSION = const(0x80)
_REG_SETUP = const(0x40)
_REG_AVERAGING = const(0x20)
_REG_RESET = const(0x10)
# Conversion: channel in bits 5:3, scan mode in bits 2:1.
_SCAN_FROM_ZERO = const(0x00)  # channels 0..N
_NO_SCAN = const(0x06)  # channel N once
# Setup: clock mode 00 (CNVST start), external single-ended reference.
_SETUP = const(_REG_SETUP | 0x04)
_UNIPOLAR_NEXT = const(0x02)  # unipolar-mode byte follows
_BIPOLAR_NEXT = const(0x03)  # bipolar-mode byte follows
_AVERAGE_ON = const(0x10)
_RESET_FIFO = const(_REG_RESET | 0x08)
_RESET_ALL = const(_REG_RESET)

_EOC_TIMEOUT_US = const(2000)  # generous: a conversion takes about 5 us


class MAX11635:
    """@brief Driver for the on-board MAX11635 12-bit ADC (U5).

    Channels 0-2 are A3-A5; channel 3 measures VBUS through a divider. Most
    programs use analog_read() and the other analog functions instead; use
    external_adc() to get the board's instance rather than making another.

    SPI bus configuration: SPI0 at 4 MHz, mode 0 (SCK GPIO22, MOSI GPIO23, MISO GPIO20, CS
    GPIO21), CNVST GPIO18, EOC GPIO19.

    External 2.048 V reference, conversions started by CNVST (clock mode 00). Making the object resets the chip.

    @ingroup ext_adc
    """

    ## Number of input channels (AIN0-AIN3).
    CHANNELS = 4
    ## Channel that measures VBUS (through the 100 kOhm / 10.2 kOhm divider).
    VBUS_CHANNEL = 3

    def __init__(self):
        """@brief Sets up SPI0 and the control pins, resets the chip and selects the external reference."""
        # 8-bit frames, MSB first: the rp2 port's defaults
        self._spi = SPI(0, baudrate=4_000_000, polarity=0, phase=0,
                        sck=Pin(22), mosi=Pin(23), miso=Pin(20))
        self._cs = Pin(21, Pin.OUT, value=1)
        self._cnvst = Pin(18, Pin.OUT, value=1)
        self._eoc = Pin(19, Pin.IN)  # low when results are ready
        self._averaging = 1
        self._write(_RESET_FIFO)
        self._write(_RESET_ALL)
        time.sleep_ms(5)
        self._write(_SETUP | _UNIPOLAR_NEXT, 0x00)  # every input single-ended
        self._write(self._averaging_byte())

    def _write(self, *data):
        self._cs(0)
        self._spi.write(bytes(data))
        self._cs(1)

    def _averaging_byte(self):
        steps = {4: 0, 8: 1, 16: 2, 32: 3}
        if self._averaging in steps:
            return _REG_AVERAGING | _AVERAGE_ON | (steps[self._averaging] << 2)
        return _REG_AVERAGING

    def _convert(self, count):
        # A CNVST low pulse starts the programmed conversions; EOC falls when
        # the results are in the chip's FIFO.
        self._cnvst(0)
        self._cnvst(1)
        start = time.ticks_us()
        while self._eoc():
            if time.ticks_diff(time.ticks_us(), start) > _EOC_TIMEOUT_US:
                raise OSError("the external ADC (MAX11635) did not respond")
        self._cs(0)
        data = self._spi.read(2 * count, 0x00)
        self._cs(1)
        return [((data[2 * i] << 8) | data[2 * i + 1]) & 0x0FFF for i in range(count)]

    @property
    def averaging(self):
        """@brief Conversions the chip averages for each result: 1, 4, 8, 16 or 32."""
        return self._averaging

    def set_averaging(self, samples):
        """@brief Sets how many conversions the chip averages for each result.

        @param samples 1 (off), 4, 8, 16 or 32; other values use the next lower one
                       (values below 1 use 1).
        @return The setting used.
        """
        for allowed in (32, 16, 8, 4, 1):
            if samples >= allowed:
                break
        self._averaging = allowed
        self._write(self._averaging_byte())
        return allowed

    def read(self, channel):
        """@brief Runs one conversion (averaged if set with set_averaging()).

        @param channel Input 0-3 (0-2 are A3-A5, 3 is VBUS).
        @return 0-4095 (0 V to 2.048 V).
        @exception ValueError The channel is not 0-3.
        @exception OSError    The chip did not respond.
        """
        if not 0 <= channel < self.CHANNELS:
            raise ValueError("channel must be 0-3")
        self._write(_REG_CONVERSION | (channel << 3) | _NO_SCAN)
        return self._convert(1)[0]

    def scan(self, last_channel=3):
        """@brief Converts channels 0 to last_channel in one scan, a few us apart.

        @param last_channel Highest channel, 0-3.
        @return A list of last_channel + 1 codes, 0-4095.
        @exception ValueError last_channel is not 0-3.
        @exception OSError    The chip did not respond.
        """
        if not 0 <= last_channel < self.CHANNELS:
            raise ValueError("last_channel must be 0-3")
        self._write(_RESET_FIFO)  # only this scan's results in the FIFO
        self._write(_REG_CONVERSION | (last_channel << 3) | _SCAN_FROM_ZERO)
        return self._convert(last_channel + 1)

    def read_differential(self, pair=0, bipolar=True):
        """@brief True differential conversion, both inputs sampled at the same instant.

        Pair 0 is AIN0 - AIN1 (A3 - A4); pair 1 is AIN2 - AIN3 (A5 - VBUS monitor).
        The pair is set back to single-ended afterwards.

        @param pair    0 or 1.
        @param bipolar True: -2048 to 2047 (-1.024 V to +1.024 V, 0.5 mV steps).
                       False: 0 to 4095 (0 V to 2.048 V; a negative difference reads 0).
        @return The code.
        @exception ValueError The pair is not 0 or 1.
        @exception OSError    The chip did not respond.
        """
        if pair not in (0, 1):
            raise ValueError("pair must be 0 or 1")
        self._write(_SETUP | (_BIPOLAR_NEXT if bipolar else _UNIPOLAR_NEXT), 0x80 >> pair)
        self._write(_REG_CONVERSION | ((2 * pair) << 3) | _NO_SCAN)
        try:
            raw = self._convert(1)[0]
        finally:
            # Back to single-ended (unipolar and bipolar registers cleared).
            self._write(_SETUP | _UNIPOLAR_NEXT, 0x00)
            self._write(_SETUP | _BIPOLAR_NEXT, 0x00)
        if bipolar and raw & 0x800:
            raw -= 4096  # 12-bit two's complement
        return raw


_ext_adc = None


def external_adc():
    """@brief Initializes _ext_adc variable for use by the user.

    The first call resets the chip and gives it the analog_averaging()
    setting. Use it for scan(), read_differential() on A5 - VBUS, or the raw
    VBUS channel; the analogue functions already cover A3-A5.

    @return The MAX11635 object (the same one every call).
    @ingroup ext_adc
    """
    global _ext_adc
    if _ext_adc is None:
        _ext_adc = MAX11635()
        _ext_adc.set_averaging(_averaging)
    return _ext_adc


# --- Analogue inputs, the same calls for A0-A5 ------------------------------------

_averaging = 1
_adcs = {}


def _analog_key(name):
    key = _name(name)
    if key not in _ANALOG:
        raise ValueError(key + " is not an analogue pin; use one of A0-A5")
    return key


def _rp2040_adc(number):
    if number not in _adcs:
        _adcs[number] = ADC(number)
    return _adcs[number]


def analog_averaging(samples):
    """@brief Averages several readings for every analogue result.

    Steadier readings, but each takes longer. A3-A5 average in the external
    ADC itself; A0-A2 take the samples one after another.

    The setting is 1 at start-up and applies to every analogue reading after the call,
    on all six pins and vbus_volts(); cpu_temperature() is not averaged. On a
    steady 1 V, going from 1 to 32 cut the spread of 100 readings from about
    16 codes to 3 on A0, and from about 10 to 1 on A3.

    @param samples 1 (off), 4, 8, 16 or 32; other values use the next lower one
                   (values below 1 use 1).
    @return The setting used.

    @par Example
    @code
    mcu.analog_averaging(16)  # average 16 samples per reading from now on
    print(mcu.analog_millivolts("A0"))  # a steadier reading
    @endcode
    @ingroup analog
    """
    global _averaging
    for allowed in (32, 16, 8, 4, 1):
        if samples >= allowed:
            break
    _averaging = allowed
    if _ext_adc is not None:
        _ext_adc.set_averaging(allowed)
    return allowed


def analog_read(name):
    """@brief Reads an analog pin as a 12-bit data.

    Inputs A0-A2 are read by the RP2040's ADC, A3-A5 by the on-board MAX11635. Each
    step is 0.8 mV on A0-A2 and 0.5 mV on A3-A5. The maximum input voltage for A0-A2
    is 3.3V, and for A3-A5 is 2.048V. An unconnected pin drifts. For a
    voltage, use analog_millivolts() or analog_volts().

    @param name "A0"-"A5".
    @return 0-4095. A0-A2: 0 = 0 V, 4095 = 3.3 V. A3-A5: 0 = 0 V, 4095 = 2.048 V.
    @exception ValueError Not an analogue pin.
    @exception OSError    The external ADC did not respond (A3-A5).
    @ingroup analog
    """
    number = PINS[_analog_key(name)]
    if number & _EXT:
        return external_adc().read(number & 0xFF)
    adc = _rp2040_adc(number)
    total = 0
    for _ in range(_averaging):
        total += adc.read_u16() >> 4
    return (total + _averaging // 2) // _averaging


def analog_full_scale_millivolts(name):
    """@brief Returns the maximum input voltage an analog pin can measure.

    @param name "A0"-"A5".
    @return 3300 for A0-A2, 2048 for A3-A5.
    @exception ValueError Not an analogue pin.
    @ingroup analog
    """
    if PINS[_analog_key(name)] & _EXT:
        return EXT_ADC_FULL_SCALE_MILLIVOLTS
    return ADC_FULL_SCALE_MILLIVOLTS


def analog_millivolts(name):
    """@brief Reads an analog pin in millivolts.

    The voltage is calculated by multiplying the value of analog_read() by the
    value of analog_full_scale_millivolts() then divided by the maximum 12bit count.
    Inputs A3-A5 are as accurate as the board's LM4040 reference, within 0.5 %.

    @param name "A0"-"A5".
    @return Voltage in mV (a float).
    @exception ValueError Not an analogue pin.
    @exception OSError    The external ADC did not respond (A3-A5).
    @ingroup analog
    """
    return analog_read(name) * analog_full_scale_millivolts(name) / 4096


def analog_volts(name):
    """@brief Reads an analog input pin in volts.

    @param name "A0"-"A5".
    @return Voltage in V (a float).
    @exception ValueError Not an analogue pin.
    @exception OSError    The external ADC did not respond (A3-A5).
    @ingroup analog
    """
    return analog_millivolts(name) / 1000


def analog_differential_millivolts(plus, minus):
    """@brief The voltage of one analog input pin minus another, in millivolts.

    A3/A4 (either order) are a true differential inputs: the external ADC
    samples both pins at the same instant, so common noise is removed from the
    measurement. The differential voltage range is +/-1024 mV in 0.5 mV steps
    for A3/A4; however, each input pins maximum voltage is still 2.048V.

    Any other combination of analog input pins will be measured in sequence, plus
    then minus. This may cause error in the measurement depending on how fast the
    signals are changing voltage. Take this into consideration when using this
    function.

    @param plus  "A0"-"A5".
    @param minus "A0"-"A5".
    @return plus - minus in mV (a float).
    @exception ValueError Not an analogue pin.
    @exception OSError    The external ADC did not respond (A3-A5).

    @par Example
    @code
    print(mcu.analog_differential_millivolts("A3", "A4"))  # A3 minus A4, sampled together
    @endcode
    @ingroup analog
    """
    p, m = _analog_key(plus), _analog_key(minus)

    if {p, m} == {"A3", "A4"}:
        code = external_adc().read_differential(0, bipolar=True)
        if -2048 < code < 2047:
            sign = 1 if p == "A3" else -1
            return sign * code * EXT_ADC_FULL_SCALE_MILLIVOLTS / 4096

    return analog_millivolts(p) - analog_millivolts(m)


_VBUS_DIVIDER = 1102 / 102  # 100 kOhm over 10.2 kOhm


def vbus_volts():
    """@brief Reads the USB input voltage supply voltage (VBUS, also on the header's VIN pin).

    The USB voltage is measured by the MAX11635 (channel 3) through a
    100 kOhm / 10.2 kOhm divider. The USB voltage can range between 5V to 20V depending on
    the power profile negotiated by the USB power delivery controller (STUSB4500). The default
    voltage is 5V unless another voltage is negotiated.

    @return Voltage in V (a float).
    @exception OSError The external ADC did not respond.
    @ingroup power
    """
    code = external_adc().read(MAX11635.VBUS_CHANNEL)
    return code * EXT_ADC_FULL_SCALE_MILLIVOLTS / 4096 * _VBUS_DIVIDER / 1000


def cpu_temperature():
    """@brief Gets the RP2040's internal temperature.

    The RP2040 has its own temperature sensor, which runs warmer than the room
    (about 10 C above it in testing). Single readings jump by a few degrees;
    average several for a steady value.

    @return Temperature in degrees Celsius (roughly +/-2 C).
    @ingroup power
    """
    volts = _rp2040_adc(4).read_u16() * 3.3 / 65535
    return 27 - (volts - 0.706) / 0.001721


# --- STUSB4500 USB Power Delivery controller --------------------------------------

_PD_ADDRESS = const(0x28)
_REG_PD_COMMAND_CTRL = const(0x1A)
_REG_DEVICE_ID = const(0x2F)
_REG_TX_HEADER_LOW = const(0x51)
_REG_PDO_COUNT = const(0x70)  # bits 2:0
_REG_SINK_PDO1 = const(0x85)  # sink PDO1-3, 4 bytes each, little-endian
_REG_RDO_STATUS = const(0x91)  # 4 bytes, little-endian
_SOFT_RESET_MESSAGE = const(0x0D)
_SEND_COMMAND = const(0x26)
_DEVICE_IDS = (0x21, 0x25)
_VOLTAGE_MASK = const(0x3FF << 10)  # bits 19:10, 50 mV units
_CURRENT_MASK = const(0x3FF)  # bits 9:0, 10 mA units
_BOARD_MAX_WATTS = 10


class STUSB4500:
    """@brief Driver for the on-board STUSB4500 USB-PD sink controller (U6).

    The STUSB4500 IC negotiates with USB-PD charger for the highest of up to
    three profiles (volts, amps) that the charger can supply. Profiles are written
    to the STUSB4500 IC working registers only, never its NVM registers, so they
    last until the board loses power. Whatever is negotiated also appears on the
    VIN pin. Use usb_pd() to get the board's instance rather than making another.

    @note Making the object raises OSError if the chip does not answer within 50 ms,
    or another device is at its address.

    @par Example
    @code
    usb = mcu.usb_pd()
    usb.request(9)          # ask for up to 9 V
    print(usb.contract())   # (volts, amps)
    @endcode
    @ingroup power
    """

    ## Number of profiles the chip holds.
    MAX_PROFILES = 3

    def __init__(self):
        """@brief Configures the I2C1 peripheral and the control pins.

        When constructing the STUSB4500 object this function trys to communicate
        with STUSB4500 IC through the I2C1 bus. If the STUSB4500 does not respond
        an OSError exception is thrown.

        @exception OSError The chip did not respond within 50 ms, or another
                           device is at its address.
        """
        self._reset = Pin(29, Pin.OUT, value=0)  # active high; keep the chip running
        self._alert = Pin(4, Pin.IN, Pin.PULL_UP)
        self._i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400_000)
        # After power-up the chip needs up to 30 ms to load its NVM before it answers.
        start = time.ticks_ms()
        while True:
            try:
                device_id = self._i2c.readfrom_mem(_PD_ADDRESS, _REG_DEVICE_ID, 1)[0]
                break
            except OSError:
                if time.ticks_diff(time.ticks_ms(), start) > 50:
                    raise OSError("the USB-PD controller (STUSB4500) did not respond")
                time.sleep_ms(2)
        if device_id not in _DEVICE_IDS:
            raise OSError("unexpected device at the USB-PD address (ID 0x%02X)" % device_id)

    def _read_u32(self, reg):
        b = self._i2c.readfrom_mem(_PD_ADDRESS, reg, 4)
        return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)

    def _write_u32(self, reg, value):
        self._i2c.writeto_mem(_PD_ADDRESS, reg, bytes(
            ((value >> 0) & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF)))

    def profiles(self):
        """@brief Gets the current active profiles.

        @return A list of (volts, amps), lowest priority first.
        @exception OSError The chip did not respond.
        """
        count = min(self._i2c.readfrom_mem(_PD_ADDRESS, _REG_PDO_COUNT, 1)[0] & 0x07,
                    self.MAX_PROFILES)
        result = []
        for i in range(count):
            pdo = self._read_u32(_REG_SINK_PDO1 + 4 * i)
            millivolts = ((pdo & _VOLTAGE_MASK) >> 10) * 50
            milliamps = (pdo & _CURRENT_MASK) * 10
            result.append((millivolts / 1000, milliamps / 1000))
        return result

    def set_profiles(self, profiles):
        """@brief Loads power profiles 1-3 and initiates a renegotiates.

        The first power profile must be 5 V (USB-PD specification rule). Each
        must be between 5V and 20 V (50 mV steps), and the current maximum is 5 A (10 mA steps)
        and at most 10 W (the board's limit). The last profile has the highest priority.

        @param profiles A list of (volts, amps), e.g. [(5, 2), (9, 1)].
        @exception ValueError A profile is out of range, or the first is not 5 V.
        @exception OSError    The chip did not respond.
        """
        if not 1 <= len(profiles) <= self.MAX_PROFILES:
            raise ValueError("give 1 to 3 profiles")
        encoded = []
        for volts, amps in profiles:
            millivolts, milliamps = round(volts * 1000), round(amps * 1000)
            if not 5000 <= millivolts <= 20000:
                raise ValueError("profile voltages must be 5-20 V")
            if not 0 <= milliamps <= 5000:
                raise ValueError("profile currents must be 0-5 A")
            if millivolts * milliamps > _BOARD_MAX_WATTS * 1_000_000:
                raise ValueError("the board is limited to %d W per profile" % _BOARD_MAX_WATTS)
            encoded.append((millivolts // 50, milliamps // 10))
        if encoded[0][0] != 100:
            raise ValueError("the first profile must be 5 V")

        current = [(round(v * 1000) // 50, round(a * 1000) // 10) for v, a in self.profiles()]
        if current == encoded:
            return  # avoids a needless renegotiation

        for i, (volts_50mv, amps_10ma) in enumerate(encoded):
            reg = _REG_SINK_PDO1 + 4 * i
            pdo = self._read_u32(reg) & ~(_VOLTAGE_MASK | _CURRENT_MASK)  # keep the flag bits
            pdo |= (volts_50mv << 10) & _VOLTAGE_MASK
            pdo |= amps_10ma & _CURRENT_MASK
            self._write_u32(reg, pdo)
        self._i2c.writeto_mem(_PD_ADDRESS, _REG_PDO_COUNT, bytes((len(encoded),)))
        self.renegotiate()

    def request(self, max_volts):
        """@brief Request renegotiation from USB-PD charger for a voltage up to max_volts.

        The charger is offered these profiles and picks the highest it can supply:
        - 5 V at 2 A, always.
        - 9 V at 1 A, if max_volts is 9 or more.
        - max_volts at 10 W, if max_volts is more than 9.

        There is nothing between 5 V and 9 V, so request(7) gives 5 V.

        @param max_volts Highest voltage to ask for, 5-20 (e.g. 5, 9, 12, 15 or 20).
        @exception ValueError max_volts is above 20 V.
        @exception OSError    The chip did not respond.
        """
        profiles = [(5, 2)]
        if max_volts >= 9:
            profiles.append((9, 1))
        if max_volts > 9:
            milliamps = _BOARD_MAX_WATTS * 1_000_000 // round(max_volts * 1000) // 10 * 10
            profiles.append((max_volts, milliamps / 1000))
        self.set_profiles(profiles)

    def renegotiate(self):
        """@brief Instructs the STUSB4550 IC renegotiate with the USB-PD charger with the current power profiles.

        @exception OSError The chip did not respond.
        """
        self._i2c.writeto_mem(_PD_ADDRESS, _REG_TX_HEADER_LOW, bytes((_SOFT_RESET_MESSAGE,)))
        self._i2c.writeto_mem(_PD_ADDRESS, _REG_PD_COMMAND_CTRL, bytes((_SEND_COMMAND,)))

    def contract_position(self):
        """@brief Gets with power profile is being used after negotiation with USB-PD charger.

        @return 1-7; 0 means no PD contract (a plain USB port or charger).

        @exception OSError The chip did not respond.
        """
        return (self._read_u32(_REG_RDO_STATUS) >> 28) & 0x07

    def contract(self):
        """@brief Reports which power profile was accepted and its current values.

        The STUSB4500 reports which offered power profile was accepted
        but not its voltage, so the voltage is measured (vbus_volts()).

        @return (volts, amps); amps is 0 when there is no PD contract.

        @exception OSError The chip or the external ADC did not respond.
        """
        rdo = self._read_u32(_REG_RDO_STATUS)
        amps = ((rdo >> 10) & 0x3FF) * 10 / 1000 if (rdo >> 28) & 0x07 else 0
        return vbus_volts(), amps


_usb_pd = None


def usb_pd():
    """@brief The board's STUSB4500, set up on first use.

    @return The STUSB4500 object (the same one every call).
    @exception OSError The chip did not respond.
    @ingroup power
    """
    global _usb_pd
    if _usb_pd is None:
        _usb_pd = STUSB4500()
    return _usb_pd


# --- Buses on the header ----------------------------------------------------------

def i2c(freq=100_000):
    """@brief Creates I2C object for control on the pins, SDA (D18) and SCL (D19).

    There are no pull-up resistors on the board for these pins: use a module
    that has them, or attach 4.7 kOhm pull-up resistors to each I2C pins. The
    on-board USB-PD controller is on a separate bus and never appears in scan().
    Call i2c() once and keep the object.

    Refer to MicroPython documentation for more information about the returned object :
    https://docs.micropython.org/en/latest/library/machine.I2C.html

    @param freq Clock in Hz: 100 kHz works with almost any module; many also run at 400 kHz.
    @return A machine.I2C.

    @par Example
    @code
    bus = mcu.i2c()
    print(bus.scan())
    @endcode

    @ingroup buses
    """
    bus = I2C(0, sda=Pin(PINS["SDA"]), scl=Pin(PINS["SCL"]), freq=freq)
    _set_d19_drive_12ma()
    return bus


def spi(baudrate=1_000_000, polarity=0, phase=0):
    """@brief Creates SPI1 object to controller the SPI bus on D13 (SCK), D11 (MOSI) and D12 (MISO).

    This function creates an SPI1 object to allow access to the SPI internal
    peripheral on the RP2040. Chipselect or multiple chipselect can be any GPIO
    pin. The chipselect pin(s) are controlled by the user.

    Refer to MicroPython documentation for more information about the returned object :
    https://docs.micropython.org/en/latest/library/machine.SPI.html

    @param baudrate Clock in Hz.
    @param polarity Clock idle level, 0 or 1.
    @param phase    0 samples on the first clock edge, 1 on the second.
    @return A machine.SPI.
    @par Example
    @code
    bus = mcu.spi()
    cs = mcu.pin("D10", "out", value=1)
    cs.value(0)
    bus.write(b"\x01\x02")
    cs.value(1)
    @endcode
    @ingroup buses
    """
    return SPI(1, baudrate=baudrate, polarity=polarity, phase=phase,
               sck=Pin(PINS["D13"]), mosi=Pin(PINS["D11"]), miso=Pin(PINS["D12"]))


def uart(number=0, baudrate=115200):
    r"""@brief Creates a UART object for use on the board header.

    Initializes UART peripheral based on the number parameter. The only valid
    number are 0 and 1. The default pins for UART0 is TX = D1 and RX = D0. For
    UART1 the default pins are TX = D4 and RX = D5.

    Refer to MicroPython documentation for more information about the returned object :
    https://docs.micropython.org/en/latest/library/machine.UART.html

    @param number   0 or 1.
    @param baudrate Bits per second; both ends must match.
    @return A machine.UART.
    @exception ValueError number is not 0 or 1.

    @par Example
    @code
    serial = mcu.uart(0)
    serial.write("hello\n")  # sends on D1
    print(serial.read())  # what has arrived on D0, or None
    @endcode
    @ingroup buses
    """
    if number == 0:
        return UART(0, baudrate=baudrate, tx=Pin(PINS["D1"]), rx=Pin(PINS["D0"]))
    if number == 1:
        return UART(1, baudrate=baudrate, tx=Pin(PINS["D4"]), rx=Pin(PINS["D5"]))
    raise ValueError("number must be 0 or 1")
