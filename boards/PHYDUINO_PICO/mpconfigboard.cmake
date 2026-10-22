# cmake file for the Phyduino Pico

# The Phyduino Pico has no pico-sdk board header upstream, so use the local
# phyduino_pico.h.
list(APPEND PICO_BOARD_HEADER_DIRS ${MICROPY_BOARD_DIR})
set(PICO_BOARD "phyduino_pico")
set(PICO_PLATFORM "rp2040")

if(NOT DEFINED MICROPY_HW_FLASH_STORAGE_BYTES)
    set(MICROPY_HW_FLASH_STORAGE_BYTES 15728640)  # PICO_FLASH_SIZE_BYTES - (1 * 1024 * 1024) = 16MB - 1MB
endif()

# Freeze phyduino.py into the firmware
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
