"""STUSB4500 profile encoding, the 10 W limit and the contract."""

import pytest

ADDR = 0x28
FLAGS = 0x2600_0000  # bits 31:20 the library must keep


def pdo(millivolts, milliamps, flags=FLAGS):
    return flags | (millivolts // 50) << 10 | milliamps // 10


def put_u32(regs, reg, value):
    regs[reg:reg + 4] = value.to_bytes(4, "little")


def get_u32(regs, reg):
    return int.from_bytes(regs[reg:reg + 4], "little")


@pytest.fixture
def chip(fake):
    regs = bytearray(256)
    regs[0x2F] = 0x25
    regs[0x70] = 3
    put_u32(regs, 0x85, pdo(5000, 2000))
    put_u32(regs, 0x89, pdo(9000, 1000))
    put_u32(regs, 0x8D, pdo(12000, 830))
    fake.I2C.devices[ADDR] = regs
    return regs


def test_bus_and_control_pins(pd, fake, chip):
    usb = pd.usb_pd()
    (bus,) = fake.I2C.instances
    assert bus.id == 1
    assert (bus.kwargs["sda"].id, bus.kwargs["scl"].id, bus.kwargs["freq"]) == (2, 3, 400_000)
    assert fake.Pin.levels[29] == 0  # RESET held low
    assert pd.usb_pd() is usb


def test_missing_chip(pd):
    with pytest.raises(OSError, match="did not respond"):
        pd.usb_pd()


def test_wrong_device_id(pd, chip):
    chip[0x2F] = 0x99
    with pytest.raises(OSError, match="0x99"):
        pd.usb_pd()


def test_profiles_decode(pd, chip):
    assert pd.usb_pd().profiles() == [(5.0, 2.0), (9.0, 1.0), (12.0, 0.83)]


def test_set_profiles_encodes_and_keeps_flags(pd, fake, chip):
    usb = pd.usb_pd()
    usb.set_profiles([(5, 1.5), (20, 0.5)])
    assert get_u32(chip, 0x85) == pdo(5000, 1500)
    assert get_u32(chip, 0x89) == pdo(20000, 500)
    assert chip[0x70] == 2
    # renegotiation: soft-reset message, then send command
    assert fake.I2C.instances[0].writes[-2:] == [(ADDR, 0x51, [0x0D]), (ADDR, 0x1A, [0x26])]


def test_set_same_profiles_skips_renegotiation(pd, fake, chip):
    pd.usb_pd().set_profiles([(5, 2), (9, 1), (12, 0.83)])
    assert fake.I2C.instances[0].writes == []


@pytest.mark.parametrize("profiles,message", [
    ([], "1 to 3"),
    ([(5, 1)] * 4, "1 to 3"),
    ([(9, 1)], "first profile must be 5 V"),
    ([(5, 2), (21, 0.4)], "5-20 V"),
    ([(5, 2), (4, 1)], "5-20 V"),
    ([(5, 6)], "0-5 A"),
    ([(5, 2), (20, 1)], "10 W"),
    ([(5, 2.1)], "10 W"),
])
def test_invalid_profiles(pd, fake, chip, profiles, message):
    with pytest.raises(ValueError, match=message):
        pd.usb_pd().set_profiles(profiles)
    assert fake.I2C.instances[0].writes == []


@pytest.mark.parametrize("max_volts,expected", [
    (5, [(5.0, 2.0)]),
    (9, [(5.0, 2.0), (9.0, 1.0)]),
    (15, [(5.0, 2.0), (9.0, 1.0), (15.0, 0.66)]),
    (20, [(5.0, 2.0), (9.0, 1.0), (20.0, 0.5)]),
])
def test_request_uses_board_profiles(pd, chip, max_volts, expected):
    usb = pd.usb_pd()
    usb.request(max_volts)
    assert usb.profiles() == expected


def test_contract(pd, fake, chip):
    usb = pd.usb_pd()
    put_u32(chip, 0x91, 2 << 28 | 100 << 10)  # offer 2, 1.00 A
    pd.external_adc()
    [s for s in fake.SPI.instances if s.id == 0][0].responses.append((1666).to_bytes(2, "big"))  # 9 V
    assert usb.contract_position() == 2
    volts, amps = usb.contract()
    assert volts == pytest.approx(9.0, abs=0.02)
    assert amps == pytest.approx(1.0)


def test_no_contract_reports_zero_amps(pd, fake, chip):
    usb = pd.usb_pd()
    put_u32(chip, 0x91, 100 << 10)  # position 0: no PD contract
    assert usb.contract_position() == 0
    assert usb.contract()[1] == 0
