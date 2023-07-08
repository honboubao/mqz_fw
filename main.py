print("Starting main.py")

import gc
import traceback
import supervisor
from mqzfw.time import now, time_diff

from keyboard.controller import setup_keyboard
from keyboard.layout import setup_layout

ble_mode = not supervisor.runtime.usb_connected

i = 0
last_exception = 0

while i < 5:
    print("Setting up keyboard")
    keyboard, status_led = setup_keyboard(ble_mode, 'Micro Qwertz BLE')
    setup_layout(keyboard)

    if __name__ != '__main__':
        break

    print("Started")

    try:
        keyboard.go()

        if i > 0 and time_diff(now(), last_exception) > 5000:
            i = 0

    except Exception as e:
        last_exception = now
        i += 1

        traceback.print_exception(error)

        try:
            error = traceback.format_exception(e)
            with open('/log.txt', 'a') as log:
                for l in error:
                    log.writelines(l)
        except Exception as log_e:
            traceback.print_exception(log_e)

        keyboard.deinit()
        status_led.deinit()
        del keyboard
        del status_led

        gc.collect()



# TODO
# (ZMK hold tap flavors)
# ble powersaving
# ble and usb
# ble multiple connections
# ble report battery level to host
# ble buffer hid reports until connected then replay
# ble explicitely enter pairing mode
# use native keypad scanner
# fix unit tests
