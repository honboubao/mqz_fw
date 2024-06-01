# Micro Qwertz Keyboard Firmware

CircuitPython keyboard firmware implementation, partly adapted from [KMK](https://github.com/KMKfw/kmk_firmware).

Purpose built for the [Micro Qwertz Keyboard hardware](https://github.com/honboubao/mqz_board) to enable the [Micro Qwertz Keyboard layout](http://www.keyboard-layout-editor.com/#/gists/12281aabe024b50dbcfd42017a9aa722).

It is tailored towards the Nordic nRF52840 SoC on a [nice!nano v2.0](https://nicekeyboards.com/nice-nano) development board.

## Dependencies

- adafruit_ble
- adafruit_dotstar

Download libraries from [https://circuitpython.org/libraries](https://circuitpython.org/libraries) for the appropriate CircuitPython version of your board (see boot_out.txt on your board) and copy the libraries to the lib folder on your board.

adafruit_dotstar is only used when running on an Adafruit ItsyBitsy nRF52840 Express. The nice!nano only has an addressable single-color blue LED on the board.

- uctypes

[uctypes](https://docs.circuitpython.org/en/latest/docs/library/ctypes.html) is needed to put the microcontroller into deep sleep. uctypes is a standard Python library implemented in the core of CircuitPython. But as of CircuitPython 9.1.0 it is not bundled with any official builds. To be able to use this feature, you need to enable uctypes in the CircuitPython source code by adding `#define MICROPY_PY_UCTYPES 1` to the `mpconfigboard.h` file of your board and create a CircuitPython build yourself and flash this build onto your board via the UF2 bootloader.

## Tests

To run unit tests in desktop environment: `python -m unittest`

# License

All software in this repository is licensed under the [GNU Public License, version 3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))
