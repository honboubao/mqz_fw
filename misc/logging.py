debug_log_enabled = False

def debug(message, *args):
    if debug_log_enabled:
        print(message.format(*args))

def set_debug_log_enabled(enabled):
    global debug_log_enabled
    debug_log_enabled = enabled