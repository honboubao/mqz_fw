from supervisor import ticks_ms
from micropython import const

_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

def now():
    return ticks_ms()

def time_add(ticks, delta):
    "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
    return (a + b) % _TICKS_PERIOD

def time_diff(ticks1, ticks2):
    "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff

def is_before(ticks1, ticks2):
    "Return true iff ticks1 is less than ticks2, assuming that they are within 2**28 ticks"
    return time_diff(ticks1, ticks2) < 0

def is_same_or_before(ticks1, ticks2):
    "Return true iff ticks1 is less than or equal to ticks2, assuming that they are within 2**28 ticks"
    return time_diff(ticks1, ticks2) <= 0