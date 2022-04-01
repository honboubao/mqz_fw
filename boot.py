import supervisor
import storage, usb_cdc

supervisor.set_next_stack_limit(4096 + 4096)

storage.disable_usb_drive()
usb_cdc.disable()