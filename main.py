print('Starting main.py')

import supervisor

running_on_board = __name__ == '__main__'

def write_log(lines):
    time = str(supervisor.ticks_ms())
    if running_on_board:
        try:
            with open('/log.txt', 'a') as log:
                for line in lines:
                    log.write(time + ': ' + line + '\n')
        except Exception as e:
            for line in lines:
                print(time + ': ' + line)
    else:
        for line in lines:
            print(time + ': ' + line)


try:
    write_log(['Booting up firmware.'])

    import asyncio
    import gc
    import traceback
    import board
    from misc.logging import set_debug_log_enabled
    from misc.time import now, time_diff
    from misc.switch import switch_pressed

    from keyboard.controller import setup_keyboard
    from keyboard.layout import setup_layout

    # TODO use nrf EVENTS_USBDETECTED register?
    ble_mode = True #not supervisor.runtime.usb_connected

    # upper right switch
    if board.board_id == 'itsybitsy_nrf52840_express':
        ble_mode = not switch_pressed(board.D13, board.A0)
    elif board.board_id == 'nice_nano' or board.board_id == 'supermini_nrf52840':
        ble_mode = not switch_pressed(board.P0_09, board.P1_06)

    set_debug_log_enabled(True)

    async def main():
        last_exception = now()

        while True:
            write_log(['Setting up keyboard'])
            keyboard, status_led, matrix, deinit = setup_keyboard(ble_mode, 'Micro Qwertz BLE')
            setup_layout(keyboard)

            if not running_on_board:
                break

            write_log(['Started'])

            try:
                keyboard_task = asyncio.create_task(keyboard.run())
                matrix_task = asyncio.create_task(matrix.run(keyboard))
                status_led_task = asyncio.create_task(status_led.run())
                await asyncio.gather(keyboard_task, matrix_task, status_led_task)
            except Exception as main_loop_exception:
                write_log(['Error in main loop.'])
                write_log(traceback.format_exception(main_loop_exception))

                deinit()
                del keyboard
                del deinit
                gc.collect()
            finally:
                if time_diff(now(), last_exception) < 5000:
                    write_log(['Too many errors within 5s, end firmware execution.'])
                    break
                last_exception = now()

    asyncio.run(main())

except Exception as setup_teardown_exception:
    write_log(['Error during setup or teardown.'])
    write_log(traceback.format_exception(setup_teardown_exception))



# TODO
# ble powersaving
# ble and usb
# ble multiple connections
# ble buffer hid reports until connected then replay
# ble explicitely enter pairing mode
# use native keypad scanner
# fix unit tests
# volume/mute keys
# properly disconnect bluetooth on error
# implement watchdog
# fix double tap repeat on symbols layer
# proper logging

# Reset into UF2 bootloader: connect via serial port, start REPL with crtl+D, execute:
# import microcontroller
# microcontroller.on_next_reset(microcontroller.RunMode.UF2)
# microcontroller.reset()

# Reset flash storage:
# import storage
# storage.erase_filesystem()
