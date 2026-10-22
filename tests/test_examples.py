"""Runs every example against the fake hardware, stopping each after a few loops."""

import pathlib
import time

import pytest

EXAMPLES = sorted((pathlib.Path(__file__).parent.parent / "examples").glob("*.py"))


class StopExample(Exception):
    pass


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_runs(pd, fake, monkeypatch, path):
    regs = bytearray(256)  # an STUSB4500 for usb_pd_power.py
    regs[0x2F] = 0x25
    regs[0x70] = 1
    regs[0x85:0x89] = (100 << 10 | 200).to_bytes(4, "little")
    fake.I2C.devices[0x28] = regs

    calls = []

    def sleep(seconds):
        calls.append(seconds)
        if len(calls) > 12:
            raise StopExample

    monkeypatch.setattr(time, "sleep", sleep)
    try:
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), {"__name__": "__main__"})
    except StopExample:
        pass
