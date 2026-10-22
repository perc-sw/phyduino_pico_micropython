// Board and hardware specific configuration
#define MICROPY_HW_BOARD_NAME "Phyduino Pico"

// machine_uart.c does not read PICO_DEFAULT_UART, so set both UARTs here.
// UART0 on D1 (TX) / D0 (RX), UART1 on D4 (TX) / D5 (RX).
#define MICROPY_HW_UART0_TX     (0)
#define MICROPY_HW_UART0_RX     (1)
#define MICROPY_HW_UART0_CTS    (-1)
#define MICROPY_HW_UART0_RTS    (-1)
#define MICROPY_HW_UART1_TX     (8)
#define MICROPY_HW_UART1_RX     (9)
#define MICROPY_HW_UART1_CTS    (-1)
#define MICROPY_HW_UART1_RTS    (-1)

// I2C1 is the on-board STUSB4500 USB-PD controller.
#define MICROPY_HW_I2C1_SDA     (2)
#define MICROPY_HW_I2C1_SCL     (3)

// SPI0 is the on-board MAX11635 ADC.
#define MICROPY_HW_SPI0_SCK     (22)
#define MICROPY_HW_SPI0_MOSI    (23)
#define MICROPY_HW_SPI0_MISO    (20)
