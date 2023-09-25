import board

from mqzfw.status_led import LED_STATUS, SimpleStatusLed, DotStarStatusLed
from mqzfw.matrix import DiodeOrientation

from mqzfw.hid import BLEHID, USBHID
from mqzfw.keyboard import Keyboard

print('board_id: ' + board.board_id)

def setup_keyboard(ble_mode, ble_name):
    # board specific stuff
    col_pins = None
    row_pins = None
    diode_orientation = None
    status_led = None

    if board.board_id == 'itsybitsy_nrf52840_express':
        status_led = DotStarStatusLed(board.APA102_SCK, board.APA102_MOSI)
        col_pins = (
            board.D2,
            board.D0,
            board.D1,
            board.D5,
            board.D7,
            board.D9,
            board.D10,
            board.D11,
            board.D12,
            board.D13,
        )
        row_pins = (board.A0, board.A1, board.A2, board.A3)
        diode_orientation = DiodeOrientation.COL2ROW

    elif board.board_id == 'nice_nano':
        status_led = SimpleStatusLed(board.LED)
        col_pins = (
            board.P0_06,
            board.P0_08,
            board.P0_17,
            board.P0_20,
            board.P0_22,
            board.P0_24,
            board.P1_00,
            board.P0_11,
            board.P1_04,
            board.P1_06,
        )
        row_pins = (board.P0_09, board.P0_10, board.P1_11, board.P1_13)
        diode_orientation = DiodeOrientation.ROW2COL

    else:
        print("Unknown board. Exit.")
        print('pins:')
        print(dir(board))
        exit()


    keyboard = Keyboard()

    keyboard.hid = BLEHID(ble_name=ble_name) if ble_mode else USBHID()
    keyboard.tapping_term = 200
    keyboard.debug_enabled = False

    keyboard.col_pins = col_pins
    keyboard.row_pins = row_pins
    keyboard.diode_orientation = diode_orientation

    if ble_mode:
        was_connected = keyboard.hid.ble.connected
        def on_tick():
            nonlocal was_connected
            if keyboard.hid.ble.connected:
                status_led.set_status(LED_STATUS.BLE_CONNECTED)
            else:
                if was_connected:
                    keyboard.hid.start_advertising()
                status_led.set_status(LED_STATUS.BLE_CONNECTING)
            was_connected = keyboard.hid.ble.connected
            status_led.tick()

        keyboard.on_tick = on_tick
    else:
        def on_tick():
            status_led.tick()

        keyboard.on_tick = on_tick
        status_led.set_status(LED_STATUS.USB_CONNECTED)

    return keyboard, status_led