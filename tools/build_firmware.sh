#!/usr/bin/env bash
# Builds MicroPython firmware for the Phyduino Pico from boards/PHYDUINO_PICO,
# with phyduino.py frozen in.
#
#   tools/build_firmware.sh          build dist/phyduino_pico-<lib>-micropython-<mp>.uf2
#   tools/build_firmware.sh clean    remove this board's build directory first
#
# Needs git, make, cmake, python3 and the Arm GNU toolchain (arm-none-eabi-gcc).
# On Ubuntu / WSL:
#   sudo apt install git make cmake python3 gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential
#
# MicroPython is cloned unchanged into build/micropython at MICROPY_VERSION.
# Change the version here deliberately and re-test on hardware.
set -euo pipefail

MICROPY_VERSION="${MICROPY_VERSION:-v1.29.0}"
MICROPY_REPO="https://github.com/micropython/micropython.git"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOARD_DIR="$ROOT/boards/PHYDUINO_PICO"
MPY_DIR="$ROOT/build/micropython"
BUILD_DIR="$ROOT/build/firmware-PHYDUINO_PICO"
JOBS="$(nproc 2>/dev/null || echo 4)"

# --- MicroPython source at the pinned version ---------------------------------------
if [ ! -d "$MPY_DIR/.git" ]; then
    git clone --depth 1 --branch "$MICROPY_VERSION" "$MICROPY_REPO" "$MPY_DIR"
fi
current="$(git -C "$MPY_DIR" describe --tags --exact-match 2>/dev/null || true)"
if [ "$current" != "$MICROPY_VERSION" ]; then
    echo "build/micropython is at '${current:-unknown}', want $MICROPY_VERSION; fetching"
    git -C "$MPY_DIR" fetch --depth 1 origin tag "$MICROPY_VERSION"
    git -C "$MPY_DIR" checkout -q "$MICROPY_VERSION"
fi

if [ "${1:-}" = "clean" ]; then
    rm -rf "$BUILD_DIR"
fi

# --- Build -----------------------------------------------------------------------
make -C "$MPY_DIR/mpy-cross" -j "$JOBS"
make -C "$MPY_DIR/ports/rp2" BOARD_DIR="$BOARD_DIR" BUILD="$BUILD_DIR" submodules
make -C "$MPY_DIR/ports/rp2" BOARD_DIR="$BOARD_DIR" BUILD="$BUILD_DIR" -j "$JOBS"

# --- Output ----------------------------------------------------------------------
lib_version="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$ROOT/phyduino.py")"
mkdir -p "$ROOT/dist"
out="$ROOT/dist/phyduino_pico-$lib_version-micropython-$MICROPY_VERSION.uf2"
cp "$BUILD_DIR/firmware.uf2" "$out"
echo "Built $out"
