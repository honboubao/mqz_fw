# Micro Qwertz Keyboard Firmware

CircuitPython keyboard firmware implementation, partly adapted from [KMK](https://github.com/KMKfw/kmk_firmware).

Purpose built for the [Micro Qwertz Keyboard hardware](https://github.com/honboubao/mqz_board) to enable the [Micro Qwertz Keyboard layout](http://www.keyboard-layout-editor.com/#/gists/12281aabe024b50dbcfd42017a9aa722).

It is tailored towards the Nordic nRF52840 SoC on a [nice!nano v2.0](https://nicekeyboards.com/nice-nano) development board.

## Dependencies

- adafruit_ble
- adafruit_dotstar

Download libraries from [https://circuitpython.org/libraries](https://circuitpython.org/libraries) for the appropriate CircuitPython version of your board (see boot_out.txt on your board) and copy the libraries to the lib folder on your board.

adafruit_dotstar is only used when running on an Adafruit ItsyBitsy nRF52840 Express. The nice!nano only has an addressable single-color blue LED on the board.

## Tests

To run unit tests in desktop environment: `python -m unittest`

# License

All software in this repository is licensed under the [GNU Public License, version 3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))
