import board
from digitalio import DigitalInOut, Direction, Pull

from mqzfw.status_led import LED_STATUS, SimpleStatusLed, DotStarStatusLed
from mqzfw.matrix import DiodeOrientation
from mqzfw.nrf_power import deep_sleep, get_battery_percentage

from mqzfw.hid import BLEHID, USBHID
from mqzfw.keyboard import Keyboard

print('board_id: ' + board.board_id)

def setup_keyboard(ble_mode, ble_name):
    # board specific stuff
    col_pins = None
    row_pins = None
    diode_orientation = None
    status_led = None
    lock_switch = None
    power_pin = None
    power_switch = None

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

    elif board.board_id == 'nice_nano' or board.board_id == 'supermini_nrf52840':
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

        lock_switch = DigitalInOut(board.P0_31)
        lock_switch.direction = Direction.INPUT
        lock_switch.pull = Pull.UP

        power_pin = board.P0_29
        power_switch = DigitalInOut(power_pin)
        power_switch.direction = Direction.INPUT
        power_switch.pull = Pull.UP

    else:
        print("Unknown board. Exit.")
        print('pins:')
        print(dir(board))
        exit()


    keyboard = Keyboard()

    keyboard.hid = BLEHID(ble_name=ble_name) if ble_mode else USBHID()
    keyboard.debug_enabled = False

    keyboard.col_pins = col_pins
    keyboard.row_pins = row_pins
    keyboard.diode_orientation = diode_orientation

    connected_led_status = LED_STATUS.BLE_CONNECTED if ble_mode else LED_STATUS.USB_CONNECTED
    connecting_led_status = LED_STATUS.BLE_CONNECTING if ble_mode else LED_STATUS.USB_CONNECTING
    was_connected = keyboard.hid.is_connected()

    def on_tick():
        battery_level = get_battery_percentage()
        if ble_mode:
            keyboard.hid.send_battery_level(battery_level)

        nonlocal was_connected
        is_connected = keyboard.hid.is_connected()
        if ble_mode and not is_connected and was_connected:
            keyboard.hid.start_advertising()
        was_connected = is_connected

        if not is_connected:
            status_led.set_status(connecting_led_status)
        elif battery_level < 10:
            status_led.set_status(LED_STATUS.LOW_BATTERY)
        else:
            status_led.set_status(connected_led_status)

        if lock_switch is not None:
            # switch position unlock (pin disconnected from ground) -> lock_switch.value = True
            # switch position lock (pin connected to ground) -> lock_switch.value = False
            keyboard.set_lock(not lock_switch.value)

        if power_switch is not None and power_pin is not None:
            # switch position off (pin disconnected from ground) -> power_switch.value = True
            # switch position on (pin connected to ground) -> power_switch.value = False
            if power_switch.value:
                deep_sleep(power_pin)

    keyboard.on_tick = on_tick

    def deinit():
        keyboard.deinit()
        status_led.deinit()

        if lock_switch is not None:
            lock_switch.deinit()

        if power_switch is not None:
            power_switch.deinit()

    return keyboard, status_led, deinit