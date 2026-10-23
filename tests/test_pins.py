"""Pin map, pin() errors, the LED and the bus helpers."""

import pytest

# From the Rev-E PCB netlist (phyduino_pico.kicad_pcb), independent of phyduino.py.
NETLIST_GPIO = {
    "D0": 1, "D1": 0, "D2": 6, "D3": 7, "D4": 8, "D5": 9, "D6": 10, "D7": 15,
    "D8": 16, "D9": 17, "D10": 13, "D11": 11, "D12": 12, "D13": 14,
    "D18": 24, "D19": 25, "SDA": 24, "SCL": 25, "LED": 5,
    "A0": 26, "A1": 27, "A2": 28,
}


def test_gpio_numbers_match_netlist(pd):
    for name, number in NETLIST_GPIO.items():
        assert pd.gpio(name) == number, name


def test_map_has_exactly_the_board_names(pd):
    assert set(pd.PINS) == set(NETLIST_GPIO) | {"A3", "A4", "A5"}


def test_names_are_not_case_sensitive(pd):
    assert pd.gpio("d7") == 15
    assert pd.gpio(" Led ") == 5


@pytest.mark.parametrize("name", ["D14", "D15", "D16", "D17"])
def test_d14_to_d17_do_not_exist(pd, name):
    with pytest.raises(ValueError, match="D0-D13, D18 and D19"):
        pd.pin(name)


def test_misspelt_name_lists_valid_names(pd):
    with pytest.raises(ValueError) as err:
        pd.pin("D77")
    assert "'D77'" in str(err.value)
    assert "D13" in str(err.value) and "A5" in str(err.value)


def test_number_instead_of_name(pd):
    with pytest.raises(TypeError, match="strings"):
        pd.pin(7)


@pytest.mark.parametrize("name", ["A3", "A4", "A5"])
def test_external_adc_pins_are_analogue_only(pd, name):
    with pytest.raises(ValueError, match="analog_read\\('" + name + "'\\)"):
        pd.pin(name)
    with pytest.raises(ValueError, match="no RP2040 GPIO"):
        pd.gpio(name)


def test_pin_modes_and_pulls(pd, fake):
    p = pd.pin("D2", "in", pull="up")
    assert (p.id, p.mode, p.pull) == (6, fake.Pin.IN, fake.Pin.PULL_UP)
    q = pd.pin("D7", "out", value=1)
    assert (q.id, q.mode, q.pull) == (15, fake.Pin.OUT, None)
    assert fake.Pin.levels[15] == 1


def test_bad_mode_or_pull(pd):
    with pytest.raises(ValueError, match="mode"):
        pd.pin("D2", "output")
    with pytest.raises(ValueError, match="pull"):
        pd.pin("D2", "in", pull="high")


GPIO25_PAD = 0x4001C004 + 4 * 25  # RP2040 PADS_BANK0 GPIO25


def test_d19_uses_12ma_drive(pd, fake):
    pd.pin("D18", "out")
    assert fake.mem32 == {}  # other pins keep the default drive
    pd.pin("D19", "out")
    assert fake.mem32[GPIO25_PAD] == 0x76  # reset value 0x56 with DRIVE (bits 5:4) = 3, 12 mA


def test_led(pd, fake):
    assert fake.Pin.created == []  # nothing touched until first use
    pd.led.on()
    assert fake.Pin.levels[5] == 1 and pd.led.value() == 1
    pd.led.toggle()
    assert fake.Pin.levels[5] == 0
    pd.led.value(1)
    pd.led.off()
    assert pd.led.value() == 0


def test_import_touches_no_hardware(pd, fake):
    assert fake.Pin.created == [] and fake.SPI.instances == [] and fake.I2C.instances == []


def test_i2c_uses_header_pins(pd, fake):
    bus = pd.i2c()
    assert bus.id == 0
    assert (bus.kwargs["sda"].id, bus.kwargs["scl"].id, bus.kwargs["freq"]) == (24, 25, 100_000)
    assert fake.mem32[GPIO25_PAD] & 0x30 == 0x30


def test_spi_uses_header_pins(pd):
    bus = pd.spi(2_000_000)
    assert bus.id == 1
    assert (bus.kwargs["sck"].id, bus.kwargs["mosi"].id, bus.kwargs["miso"].id) == (14, 11, 12)
    assert bus.kwargs["baudrate"] == 2_000_000


def test_uarts_use_header_pins(pd):
    u0, u1 = pd.uart(0), pd.uart(1, 9600)
    assert (u0.id, u0.kwargs["tx"].id, u0.kwargs["rx"].id) == (0, 0, 1)
    assert (u1.id, u1.kwargs["tx"].id, u1.kwargs["rx"].id, u1.kwargs["baudrate"]) == (1, 8, 9, 9600)
    with pytest.raises(ValueError):
        pd.uart(2)


def test_pwm_sets_up_pin_frequency_and_duty(pd, fake):
    glow = pd.pwm("LED")
    assert (glow.pin.id, glow.pin.mode, glow.freq(), glow.duty_u16()) == (5, fake.Pin.OUT, 1000, 0)
    buzzer = pd.pwm("d3", freq=440, duty_u16=32768)
    assert (buzzer.pin.id, buzzer.freq(), buzzer.duty_u16()) == (7, 440, 32768)


def test_pwm_on_d19_uses_12ma_drive(pd, fake):
    pd.pwm("D19")
    assert fake.mem32[GPIO25_PAD] & 0x30 == 0x30


@pytest.mark.parametrize("name", ["A3", "A4", "A5"])
def test_pwm_not_on_external_adc_pins(pd, name):
    with pytest.raises(ValueError, match="external ADC"):
        pd.pwm(name)


@pytest.mark.parametrize("first, second", [
    ("D1", "D8"), ("D0", "D9"), ("D4", "D18"), ("D5", "D19"),
    ("D6", "A0"), ("D11", "A1"), ("D12", "A2"),
])
def test_pwm_refuses_shared_output(pd, first, second):
    pd.pwm(first)
    with pytest.raises(ValueError, match=first):
        pd.pwm(second)
    pd.pin(first, "out")  # frees the output
    pd.pwm(second)


def test_pwm_same_pin_again_or_by_other_name(pd):
    pd.pwm("D18")
    pd.pwm("D18", freq=50)
    pd.pwm("SDA")


def test_pwm_slice_neighbours_allowed(pd):
    pd.pwm("D2")
    pd.pwm("D3")
