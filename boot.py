import supervisor
import storage
import usb_cdc
import board
from misc.switch import switch_pressed

if (board.board_id == 'nice_nano' or board.board_id == 'supermini_nrf52840') and switch_pressed(board.P0_09, board.P0_06) and switch_pressed(board.P1_11, board.P0_06):
    import microcontroller
    microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
    microcontroller.reset()

# supervisor.set_next_stack_limit(4096 + 4096)

supervisor.runtime.ble_workflow = True

debug = True

# upper left switch
if board.board_id == 'itsybitsy_nrf52840_express':
    debug = switch_pressed(board.D2, board.A0)
elif board.board_id == 'nice_nano' or board.board_id == 'supermini_nrf52840':
    debug = switch_pressed(board.P0_09, board.P0_06)

#debug = True
if not debug:
    # mount for writing
    storage.remount("/", False)

    # hide usb storage drive
    storage.disable_usb_drive()

    # disable serial port
    # usb_cdc.disable()