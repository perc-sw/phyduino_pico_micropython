"""MAX11635 command bytes and the analogue functions for A0-A5."""

import pytest

INIT = [[0x18], [0x10], [0x46, 0x00], [0x20]]  # reset FIFO, reset all, single-ended setup, averaging off


def ext_spi(fake):
    (spi,) = [s for s in fake.SPI.instances if s.id == 0]
    return spi


def code_bytes(*codes):
    return bytes(b for c in codes for b in (c >> 8, c & 0xFF))


def test_spi_set_up(pd, fake):
    pd.external_adc()
    spi = ext_spi(fake)
    assert spi.kwargs["baudrate"] == 4_000_000
    assert (spi.kwargs["polarity"], spi.kwargs["phase"]) == (0, 0)
    assert (spi.kwargs["sck"].id, spi.kwargs["mosi"].id, spi.kwargs["miso"].id) == (22, 23, 20)
    assert fake.Pin.levels[21] == 1 and fake.Pin.levels[18] == 1  # CS and CNVST idle high


def test_set_up_sequence_uses_external_reference(pd, fake):
    pd.external_adc()
    assert ext_spi(fake).writes[:4] == INIT
    assert INIT[2][0] & 0x0C == 0x04  # REFSEL = 01: external single-ended reference


def test_created_on_first_a3_read_only(pd, fake):
    fake.ADC.values[26] = 0x8000
    pd.analog_read("A0")
    assert fake.SPI.instances == []
    pd.analog_read("A3")
    assert len(fake.SPI.instances) == 1


@pytest.mark.parametrize("name,channel", [("A3", 0), ("A4", 1), ("A5", 2)])
def test_read_sends_conversion_byte(pd, fake, name, channel):
    adc = pd.external_adc()
    spi = ext_spi(fake)
    spi.writes.clear()
    spi.responses.append(code_bytes(0xF123))  # top four bits must be ignored
    assert pd.analog_read(name) == 0x123
    assert spi.writes == [[0x80 | channel << 3 | 0x06]]
    assert adc.averaging == 1


def test_eoc_timeout_raises(pd, fake, fake_clock):
    pd.external_adc()
    fake.Pin.levels[19] = 1  # EOC never falls
    fake_clock.step_us = 100
    with pytest.raises(OSError, match="MAX11635"):
        pd.analog_read("A3")


def test_millivolt_conversions(pd, fake):
    fake.ADC.values[26] = 4095 << 4
    assert pd.analog_read("A0") == 4095
    assert pd.analog_millivolts("A0") == pytest.approx(4095 * 3300 / 4096)
    pd.external_adc()
    ext_spi(fake).responses.append(code_bytes(2048))
    assert pd.analog_volts("A3") == pytest.approx(1.024)
    assert pd.analog_full_scale_millivolts("a1") == 3300
    assert pd.analog_full_scale_millivolts("A5") == 2048


def test_analog_on_digital_pin(pd):
    with pytest.raises(ValueError, match="not an analogue pin"):
        pd.analog_read("D7")


@pytest.mark.parametrize("asked,used,byte", [(1, 1, 0x20), (4, 4, 0x30), (10, 8, 0x34),
                                             (16, 16, 0x38), (100, 32, 0x3C), (0, 1, 0x20)])
def test_averaging_bytes(pd, fake, asked, used, byte):
    pd.external_adc()
    spi = ext_spi(fake)
    spi.writes.clear()
    assert pd.analog_averaging(asked) == used
    assert spi.writes == [[byte]]


def test_averaging_applies_when_adc_created_later(pd, fake):
    pd.analog_averaging(16)
    pd.external_adc()
    assert ext_spi(fake).writes[-1] == [0x38]


def test_rp2040_pins_average_in_software(pd, fake):
    pd.analog_averaging(4)
    fake.ADC.values[27] = 1001 << 4
    assert pd.analog_read("A1") == 1001


def test_scan(pd, fake):
    adc = pd.external_adc()
    spi = ext_spi(fake)
    spi.writes.clear()
    spi.responses.append(code_bytes(1, 2, 3, 4))
    assert adc.scan(3) == [1, 2, 3, 4]
    assert spi.writes == [[0x18], [0x80 | 3 << 3 | 0x00]]


def test_vbus(pd, fake):
    pd.external_adc()
    spi = ext_spi(fake)
    spi.writes.clear()
    spi.responses.append(code_bytes(926))  # 5 V / 10.804 = 0.4628 V
    assert pd.vbus_volts() == pytest.approx(5.0, abs=0.01)
    assert spi.writes == [[0x80 | 3 << 3 | 0x06]]


def test_true_differential_a3_a4(pd, fake):
    pd.external_adc()
    spi = ext_spi(fake)
    spi.writes.clear()
    spi.responses.append(code_bytes(0x1000 - 200))  # -200 in 12-bit two's complement
    assert pd.analog_differential_millivolts("A3", "A4") == pytest.approx(-100.0)
    # bipolar mode for pair 0, convert channel 0, then back to single-ended
    assert spi.writes == [[0x47, 0x80], [0x86], [0x46, 0x00], [0x47, 0x00]]
    spi.responses.append(code_bytes(0x1000 - 200))
    assert pd.analog_differential_millivolts("A4", "A3") == pytest.approx(100.0)


def test_differential_out_of_range_falls_back(pd, fake):
    pd.external_adc()
    spi = ext_spi(fake)
    spi.responses += [code_bytes(2047), code_bytes(4000), code_bytes(100)]
    assert pd.analog_differential_millivolts("A3", "A4") == pytest.approx((4000 - 100) * 2048 / 4096)


def test_differential_other_pairs_subtract(pd, fake):
    fake.ADC.values[26] = 3000 << 4
    fake.ADC.values[27] = 1000 << 4
    assert pd.analog_differential_millivolts("A0", "A1") == pytest.approx(2000 * 3300 / 4096)
    assert fake.SPI.instances == []


def test_differential_returns_to_single_ended_after_timeout(pd, fake, fake_clock):
    adc = pd.external_adc()
    spi = ext_spi(fake)
    spi.writes.clear()
    fake.Pin.levels[19] = 1
    fake_clock.step_us = 100
    with pytest.raises(OSError):
        adc.read_differential(0)
    assert spi.writes[-2:] == [[0x46, 0x00], [0x47, 0x00]]


def test_cpu_temperature(pd, fake):
    fake.ADC.values[4] = round(0.706 / 3.3 * 65535)
    assert pd.cpu_temperature() == pytest.approx(27, abs=0.1)
