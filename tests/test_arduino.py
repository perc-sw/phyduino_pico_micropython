"""arduino.py: Arduino-style names and ranges on top of phyduino.py."""

import pytest


def test_pin_numbers_and_names(ard, fake):
    ard.pinMode(13, ard.OUTPUT)
    ard.pinMode("d2", ard.INPUT_PULLUP)
    ard.pinMode(ard.LED_BUILTIN, ard.OUTPUT)
    assert [(c[0], c[1], c[2]) for c in fake.Pin.created] == [
        (14, fake.Pin.OUT, None), (6, fake.Pin.IN, fake.Pin.PULL_UP), (5, fake.Pin.OUT, None)]


@pytest.mark.parametrize("pin", [14, 3.5, "A3"])
def test_bad_pins(ard, pin):
    with pytest.raises((ValueError, TypeError)):
        ard.pinMode(pin, ard.INPUT)


def test_bad_mode(ard):
    with pytest.raises(ValueError, match="INPUT_PULLUP"):
        ard.pinMode(2, "out")


def test_digital_write_and_read(ard, fake):
    ard.pinMode(7, ard.OUTPUT)
    ard.digitalWrite(7, ard.HIGH)
    assert fake.Pin.levels[15] == 1
    assert ard.digitalRead(7) == ard.HIGH
    ard.digitalWrite(7, ard.LOW)
    assert ard.digitalRead(7) == ard.LOW
    assert len(fake.Pin.created) == 1  # the pin is set up once, not on every call


def test_digital_write_makes_an_output(ard, fake):
    ard.pinMode(7, ard.INPUT)
    ard.digitalWrite(7, ard.HIGH)
    assert fake.Pin.created[-1][1] == fake.Pin.OUT
    assert fake.Pin.levels[15] == 1


def test_digital_read_makes_an_input(ard, fake):
    fake.Pin.levels[6] = 1
    assert ard.digitalRead(2) == ard.HIGH
    assert fake.Pin.created == [(6, fake.Pin.IN, None, {})]


def test_analog_read_default_10_bits(ard, fake):
    fake.ADC.values[26] = 0xFFF0  # 4095 as a 12-bit code
    assert ard.analogRead(ard.A0) == 1023
    assert ard.analogRead(0) == 1023  # 0-5 are A0-A5


@pytest.mark.parametrize("bits, result", [(8, 255), (12, 4095), (16, 65520)])
def test_analog_read_resolution(ard, fake, bits, result):
    fake.ADC.values[26] = 0xFFF0
    ard.analogReadResolution(bits)
    assert ard.analogRead("A0") == result


def test_analog_read_external_adc(pd, ard, fake):
    pd.external_adc()
    fake.SPI.instances[0].responses.append(bytes([0x0F, 0xFF]))  # 4095
    assert ard.analogRead(3) == 1023


def test_analog_read_digital_pin(ard):
    with pytest.raises(ValueError, match="not an analogue pin"):
        ard.analogRead("D2")


def test_analog_write(ard, fake):
    ard.analogWrite(3, 255)
    p = fake.PWM.instances[0]
    assert (p.pin.id, p.frequency, p.duty) == (7, 1000, 65535)
    ard.analogWrite(3, 128)
    assert p.duty == 128 * 65535 // 255
    ard.analogWrite(3, 300)  # clamped
    assert p.duty == 65535
    ard.analogWrite(3, -1)
    assert p.duty == 0
    assert len(fake.PWM.instances) == 1  # reused, not set up again


def test_analog_write_resolution_and_freq(ard, fake):
    ard.analogWriteResolution(10)
    ard.analogWriteFreq(500)
    ard.analogWrite(3, 1023)
    p = fake.PWM.instances[0]
    assert (p.frequency, p.duty) == (500, 65535)


def test_digital_write_after_analog_write(ard, fake):
    ard.analogWrite(3, 100)
    ard.digitalWrite(3, ard.HIGH)
    assert fake.Pin.created[-1][:2] == (7, fake.Pin.OUT)
    ard.analogWrite(3, 50)  # back on PWM
    assert len(fake.PWM.instances) == 2


def test_analog_write_shared_output(ard):
    ard.analogWrite(1, 10)
    with pytest.raises(ValueError, match="share a PWM output"):
        ard.analogWrite(8, 10)  # D1/D8 share one


@pytest.mark.parametrize("bits", [0, 17])
def test_bad_resolution(ard, bits):
    with pytest.raises(ValueError):
        ard.analogReadResolution(bits)
    with pytest.raises(ValueError):
        ard.analogWriteResolution(bits)


def test_tone_and_no_tone(ard, fake):
    ard.tone(8, 440)
    p = fake.PWM.instances[0]
    assert (p.pin.id, p.frequency, p.duty) == (16, 440, 32768)
    assert fake.Timer.instances == []
    ard.noTone(8)
    assert p.duty == 0


def test_tone_duration_stops_itself(ard, fake):
    ard.tone(8, 262, 250)
    timer = fake.Timer.instances[0]
    assert (timer.mode, timer.period) == (fake.Timer.ONE_SHOT, 250)
    timer.fire()
    assert fake.PWM.instances[0].duty == 0


def test_new_tone_cancels_old_stop(ard, fake):
    ard.tone(8, 262, 250)
    ard.tone(8, 330)
    assert not fake.Timer.instances[0].running
    assert fake.PWM.instances[0].duty == 32768


def test_tone_zero_is_silence(ard, fake):
    ard.tone(8, 262)
    ard.tone(8, 0)
    assert fake.PWM.instances[0].duty == 0


def test_no_tone_on_unused_pin(ard, fake):
    ard.noTone(8)
    assert fake.PWM.instances == []


def test_delay_and_millis(ard, fake_clock):
    start = ard.millis()
    ard.delay(250)
    assert ard.millis() - start == 250
    start = ard.micros()
    ard.delayMicroseconds(40)
    assert 40 <= ard.micros() - start <= 42  # each fake clock read adds 1 us


def test_millis_does_not_wrap(ard, monkeypatch):
    import time

    period = 1 << 30  # MicroPython's ticks wrap here
    readings = iter([period - 10, 5, 100_000])
    monkeypatch.setattr(time, "ticks_ms", lambda: next(readings))
    monkeypatch.setattr(time, "ticks_diff",
                        lambda new, old: ((new - old + period // 2) % period) - period // 2)
    ard._last_ms, ard._millis = period - 20, period - 20
    assert ard.millis() == period - 10
    assert ard.millis() == period + 5  # across the wrap
    assert ard.millis() == period + 100_000


@pytest.mark.parametrize("args, result", [
    ((512, 0, 1023, 0, 255), 127),
    ((0, 0, 1023, 0, 255), 0),
    ((1023, 0, 1023, 0, 255), 255),
    ((5, 0, 10, 100, 0), 50),       # a reversed range
    ((-3, 0, 10, 0, 4), -1),        # rounds towards zero, as on an Arduino
    ((20, 0, 10, 0, 100), 200),     # not clamped
    ((0.5, 0, 1, 0, 3.3), 1.65),
])
def test_map(ard, args, result):
    assert ard.map(*args) == pytest.approx(result)
    assert type(ard.map(*args)) is type(result)


def test_constrain(ard):
    assert ard.constrain(5, 0, 10) == 5
    assert ard.constrain(-1, 0, 10) == 0
    assert ard.constrain(11, 0, 10) == 10
