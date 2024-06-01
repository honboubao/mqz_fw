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
        # board layout and pin names:
        #               USB C
        #           +---#####---+
        #  TX/P0_06 |   #####   | P0_04/AIN2/BAT_VOLT (BAT IN)
        #  RX/P0_08 |           | (GND)
        #     (GND) | o         | (RST)
        #     (GND) |           | P0_13/VCC_OFF (VCC 3.3V)
        # SDA/P0_17 |   w       | P0_31/AIN7
        # SCL/P0_20 | x         | P0_29/AIN5
        #     P0_22 |           | P0_02/AIN0
        #     P0_24 |           | P1_15
        #     P1_00 | y z       | P1_13/SCK
        #     P0_11 | a b c     | P1_11/MISO
        #     P1_04 |           | P0_10/NFC2/MOSI
        #     P1_06 +-----------+ P0_09/NFC1
        #
        # a: P1_01
        # b: P1_02
        # c: P1_07
        # w: P0_26 (only on nice!nano v1.0)
        # x: P0_12 (only on nice!nano v1.0)
        # y: (SWD)
        # z: (SWC)
        # o: P0_15/LED
        #
        # additional singleton names: I2C (SCL/SDA), SPI (SCK/MOSI/MISO), UART (RX/TX)
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