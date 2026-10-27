# Prints the printable ASCII characters, 33 ("!") to 126 ("~"), each with its
# value in decimal, hexadecimal, octal and binary.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    print("ASCII Table ~ Character Map")
    for code in range(33, 127):  # 33 up to 126; range() stops before its second number
        # chr() gives the character for a code. %d is decimal, %x hexadecimal and
        # %o octal; bin() gives "0b100001", and [2:] drops the "0b".
        print("%s, dec: %d, hex: %x, oct: %o, bin: %s" % (chr(code), code, code, code, bin(code)[2:]))


def loop():
    delay(1000)  # nothing left to do: the table was printed once, in setup()


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until you press Ctrl-C (or Stop in your editor)
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
