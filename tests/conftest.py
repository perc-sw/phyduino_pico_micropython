"""Loads phyduino.py on the PC with fake `machine`, `micropython` and `time` functions."""

import importlib
import os
import sys
import time
import types

import pytest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import fake_machine  # noqa: E402

sys.modules["machine"] = fake_machine
sys.modules["micropython"] = types.SimpleNamespace(const=lambda value: value)


class FakeClock:
    """MicroPython's ticks functions; each read moves time on by `step_us`."""

    def __init__(self):
        self.now_us = 0
        self.step_us = 1

    def ticks_us(self):
        self.now_us += self.step_us
        return self.now_us

    def ticks_ms(self):
        return self.ticks_us() // 1000

    def sleep_ms(self, ms):
        self.now_us += ms * 1000


clock = FakeClock()
time.ticks_us = clock.ticks_us
time.ticks_ms = clock.ticks_ms
time.ticks_diff = lambda new, old: new - old
time.sleep_ms = clock.sleep_ms


@pytest.fixture
def pd():
    """A freshly loaded phyduino module with clean fake hardware."""
    fake_machine.reset()
    clock.now_us = 0
    clock.step_us = 1
    import phyduino

    return importlib.reload(phyduino)


@pytest.fixture
def fake():
    return fake_machine


@pytest.fixture
def fake_clock():
    return clock
