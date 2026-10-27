"""Runs every example against the fake hardware.

examples/arduino/: setup() once, then loop() a few times.
examples/phyduino/: the script itself, until it has run LINES lines of its own
(its `while True:` never ends) or it finishes.
"""

import io
import pathlib
import sys
import time

import pytest

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"
ARDUINO = sorted(EXAMPLES_DIR.glob("arduino/*/*/main.py"))  # examples/arduino/<category>/<name>/main.py
PHYDUINO = sorted(EXAMPLES_DIR.glob("phyduino/*/*/main.py"))  # examples/phyduino/<category>/<name>/main.py
LOOPS = 20
LINES = 20_000


def _ids(path):
    return path.relative_to(EXAMPLES_DIR).as_posix()


def test_examples_are_main_py_in_their_own_folder():
    scripts = sorted(EXAMPLES_DIR.rglob("*.py"))
    assert scripts == sorted(ARDUINO + PHYDUINO)  # MicroPython runs main.py at start-up, so no other names
    assert len(ARDUINO) == len(PHYDUINO) == 25


def test_both_sets_have_the_same_examples():
    assert [p.relative_to(EXAMPLES_DIR / "arduino") for p in ARDUINO] == \
        [p.relative_to(EXAMPLES_DIR / "phyduino") for p in PHYDUINO]


@pytest.fixture
def hardware(ard, fake, fake_clock, monkeypatch):
    regs = bytearray(256)  # an STUSB4500 for usb_pd_power
    regs[0x2F] = 0x25
    regs[0x70] = 1
    regs[0x85:0x89] = (100 << 10 | 200).to_bytes(4, "little")
    fake.I2C.devices[0x28] = regs

    monkeypatch.setattr(time, "sleep", lambda seconds: fake_clock.sleep_ms(seconds * 1000))
    monkeypatch.setattr(sys, "stdin", io.StringIO("HL" * LOOPS))  # for physical_pixel


@pytest.mark.parametrize("path", ARDUINO, ids=_ids)
def test_arduino_example_runs(hardware, path):
    source = path.read_text(encoding="utf-8")
    assert "from arduino import *" in source
    example = {"__name__": "example"}  # not "__main__", so main() does not start
    exec(compile(source, str(path), "exec"), example)
    assert callable(example["main"])
    example["setup"]()
    for _ in range(LOOPS):
        example["loop"]()


class _Stop(Exception):
    """Raised once a phyduino example has run LINES lines."""


@pytest.mark.parametrize("path", PHYDUINO, ids=_ids)
def test_phyduino_example_runs(hardware, path):
    source = path.read_text(encoding="utf-8")
    assert "arduino" not in source and "def setup" not in source and "def loop" not in source
    filename = str(path)
    lines = 0

    def count(frame, event, arg):
        nonlocal lines
        if event == "line":
            lines += 1
            if lines > LINES:
                raise _Stop
        return count

    sys.settrace(lambda frame, event, arg: count if frame.f_code.co_filename == filename else None)
    try:
        exec(compile(source, filename, "exec"), {"__name__": "__main__"})
    except _Stop:
        pass  # still looping: it ran without an error
    finally:
        sys.settrace(None)
    assert lines > 0
