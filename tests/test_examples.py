"""Runs every example against the fake hardware: setup() once, then loop() a few times."""

import io
import pathlib
import sys
import time

import pytest

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.glob("*/*.py"))
LOOPS = 20


def test_example_names_are_unique():
    names = [path.name for path in EXAMPLES]
    assert len(names) == len(set(names))  # Doxygen finds examples by file name


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.relative_to(EXAMPLES_DIR).as_posix())
def test_example_runs(pd, fake, fake_clock, monkeypatch, path):
    regs = bytearray(256)  # an STUSB4500 for usb_pd_power.py
    regs[0x2F] = 0x25
    regs[0x70] = 1
    regs[0x85:0x89] = (100 << 10 | 200).to_bytes(4, "little")
    fake.I2C.devices[0x28] = regs

    monkeypatch.setattr(time, "sleep", lambda seconds: fake_clock.sleep_ms(seconds * 1000))
    monkeypatch.setattr(sys, "stdin", io.StringIO("HL" * LOOPS))  # for physical_pixel.py

    example = {"__name__": "example"}  # not "__main__", so main() does not start
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), example)
    assert callable(example["main"])
    example["setup"]()
    for _ in range(LOOPS):
        example["loop"]()
