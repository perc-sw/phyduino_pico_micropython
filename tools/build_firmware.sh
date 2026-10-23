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

# In WSL, PATH includes Windows programs (/mnt/...), and a Windows picotool.exe
# can't open the build's Linux paths. Leave them out so pico-sdk builds its own
# picotool, and drop a Windows picotool remembered by an earlier build.
PATH="$(printf '%s' "$PATH" | tr ':' '\n' | grep -v '^/mnt/' | paste -sd: -)"
if [ -f "$BUILD_DIR/CMakeCache.txt" ]; then
    sed -i 's#^picotool_DIR:PATH=/mnt/.*#picotool_DIR:PATH=picotool_DIR-NOTFOUND#' "$BUILD_DIR/CMakeCache.txt"
fi

# Submodules this board needs (the rp2 port's list, without the wireless ones).
# Fetched here so git can show its progress; make's own submodule step hides it,
# and still runs afterwards to fetch anything missing from this list.
SUBMODULES=(lib/pico-sdk lib/tinyusb lib/mbedtls lib/micropython-lib)

# Prints a step heading with the time since the script started
step() {
    printf '\n==> [%s] %s (%dm%02ds)\n' "$1" "$2" $((SECONDS / 60)) $((SECONDS % 60))
}

# --- MicroPython source at the pinned version ---------------------------------------
step 1/5 "MicroPython $MICROPY_VERSION source"
if [ ! -d "$MPY_DIR/.git" ]; then
    echo "Downloading MicroPython into build/micropython"
    git clone --depth 1 --branch "$MICROPY_VERSION" "$MICROPY_REPO" "$MPY_DIR"
else
    echo "Using build/micropython"
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

# --- Submodules --------------------------------------------------------------------
step 2/5 "Submodules (first build only; can take a few minutes)"
n=0
for sub in "${SUBMODULES[@]}"; do
    n=$((n + 1))
    if [ -e "$MPY_DIR/$sub/.git" ]; then
        echo "($n/${#SUBMODULES[@]}) $sub: already downloaded"
    else
        echo "($n/${#SUBMODULES[@]}) Downloading $sub"
        git -C "$MPY_DIR" submodule update --init --filter=blob:none "$sub"
    fi
done
echo "Checking for any other submodules the board needs"
make -C "$MPY_DIR/ports/rp2" BOARD_DIR="$BOARD_DIR" BUILD="$BUILD_DIR" submodules > "$BUILD_DIR.submodules.log" 2>&1 ||
    { cat "$BUILD_DIR.submodules.log"; exit 1; }

# --- Build -----------------------------------------------------------------------
step 3/5 "mpy-cross (compiles the frozen phyduino.py)"
make -C "$MPY_DIR/mpy-cross" -j "$JOBS"

step 4/5 "Firmware, $JOBS jobs"
make -C "$MPY_DIR/ports/rp2" BOARD_DIR="$BOARD_DIR" BUILD="$BUILD_DIR" -j "$JOBS"

# --- Output ----------------------------------------------------------------------
step 5/5 "UF2"
lib_version="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$ROOT/phyduino.py")"
mkdir -p "$ROOT/dist"
out="$ROOT/dist/phyduino_pico-$lib_version-micropython-$MICROPY_VERSION.uf2"
cp "$BUILD_DIR/firmware.uf2" "$out"
echo "Built $out in $((SECONDS / 60))m$((SECONDS % 60))s"
