print("Starting main.py")

import supervisor

from keyboard.controller import setup_keyboard
from keyboard.layout import setup_layout

ble_mode = not supervisor.runtime.usb_connected

while True:
    print("Setting up keyboard")
    keyboard = setup_keyboard(ble_mode, 'Micro Qwertz BLE')
    setup_layout(keyboard)

    if __name__ != '__main__':
        break

    print("Started")

    try:
        keyboard.go()
    except Exception as e:
        print(e)


# TODO
# (ZMK hold tap flavors)
# hide circuitpy drive/show on special key
# ble powersaving
# ble and usb
# ble multiple connections
# ble report battery level to host
# ble buffer hid reports until connected then replay
# ble explicitely enter pairing mode
# use native keypad scanner