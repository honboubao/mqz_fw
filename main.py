print("Starting")

import board
import adafruit_dotstar
import supervisor
from mqzfw.hid import BLEHID, USBHID

ble_mode = not supervisor.runtime.usb_connected

pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
pixels[0] = (1, 0, 0, 0.05) # red

from mqzfw.keycodes import *
from mqzfw.keys import Key, KeyboardKey
from mqzfw.keyboard import Keyboard
from mqzfw.matrix import DiodeOrientation

keyboard = Keyboard()
if ble_mode:
    keyboard.hid = BLEHID(ble_name='Micro Qwertz BLE')
else:
    keyboard.hid = USBHID()
keyboard.tapping_term = 200
keyboard.debug_enabled = False

keyboard.col_pins = (
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
keyboard.row_pins = (board.A0, board.A1, board.A2, board.A3)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

_ = XXXX
____ = XXXX
BASE = 0
NUM = 1
SYM = 2
FN = 3
NAV = 4
LOCK = 5

UNDO = KeyboardKey(Z.keycode, KC_LCTL)
CUT = KeyboardKey(X.keycode, KC_LCTL)
COPY = KeyboardKey(C.keycode, KC_LCTL)
PAST = KeyboardKey(V.keycode, KC_LCTL)
MNAV = MO(NAV)
LNUM = TO(NUM)
LSYM = TO(SYM)
LFN = TO(FN)
LNAV = TO(NAV)
DTSS = SO(DOT, ß)
BSDL = SO(BKSP, DEL, ignore_caps=True)
ATAB = KeyboardKey(TAB.keycode)
CTAB = KeyboardKey(TAB.keycode)
ACTMOD = KeyboardKey(None)


def transform_modkey(key, mod, layer):
    if key in (LSFT, LCTL, LWIN, LALT):
        return key

    if isinstance(mod, Key) and mod.mods > 0:
        return MT(mod, key)
    if isinstance(mod, int) and (mod == LOCK or layer == 0):
        return LT(mod, key)
    return key

def apply_modtaps(keymap, layer):
    return [transform_modkey(key, mod, layer) for key, mod in zip(keymap, modtaps)]

modtaps = [ # mod taps
        ____, ____, FN,   ____, ____, ____, ____, FN,   ____, ____,
        LSFT, SYM,  NUM,  ____, ____, LOCK, ____, NUM,  SYM,  RSFT,
        LCTL, LWIN, LALT, ____, NUM,  ____, ____, RALT, RWIN, RCTL,
        _,    _,    _,    ____, _,    ____, _,    _,    _,    _
    ]
keyboard.keymap = [apply_modtaps(keymap, layer) for layer, keymap in enumerate([
    [ # base
        Q,    W,    E,    R,    T,    Z,    U,    I,    O,    P,
        A,    S,    D,    F,    G,    H,    J,    K,    L,    Ö,
        Y,    X,    C,    V,    B,    N,    M,    Ü,    DTSS, Ä,
        _,    _,    _,    MNAV, _,     SPC,  _,    _,    _,    _
    ],
    [ # num
        DEG,  SECT, SUP2, SUP3, ____, COLN, N7,   N8,   N9,   BKSP,
        EURO, ACUT, MICR, SPC,  ____, COMM, N4,   N5,   N6,   ENT,
        TILD, ____, ____, ____, ____, DOT,  N1,   N2,   N3,   MINS,
        _,    _,    _,    MNAV, _,     N0,   _,    _,    _,    _
    ],
    [ # sym
        CIRC, DLR,  HASH, PERC, AMPR, PIPE, LCBR, RCBR, LBRC, RBRC,
        AT,   GRV,  QUOT, DQUO, QUES, EXLM, LPRN, RPRN, LABK, RABK,
        BSLS, SLSH, ASTR, PLUS, MINS, EQL,  SCLN, COMM, COLN, UNDS,
        _,    _,    _,    MNAV, _,     SPC,  _,    _,    _,    _
    ],
    [ # fn
        ____, ____, ____, ____, INS,  SLCK, F7,   F8,   F9,   F10,
        LSFT, ____, ____, ____, PSCR, PAUS, F4,   F5,   F6,   F11,
        LCTL, LWIN, LALT, ____, APP,  ____, F1,   F2,   F3,   F12,
        _,    _,    _,    MNAV, _,     SPC,  _,    _,    _,    _
    ],
    [ # nav
        CTAB, HOME, UP,   END,  UNDO,  PGUP, HOME, UP,   END,  BSDL,
        ATAB, LEFT, DOWN, RGHT, ENT,   PGDN, LEFT, DOWN, RGHT, ENT,
        ESC,  TAB,  BKSP, DEL,  MBBK,  MBFW, CUT,  COPY, PAST, ESC,
        _,    _,    _,    MNAV, _,     TAB,  _,    _,    _,    _
    ],
    [ # lock
        ____, ____, LFN,  ____, ____, ____, ____, ____, ____, ____,
        CAPS, LSYM, LNUM, ____, ____, ____, ____, LNUM, LSYM, CAPS,
        ____, ____, ____, ____, LNUM, ____, ____, ____, ____, ____,
        _,    _,    _,    LNAV, _,    CLLK, _,    _,    _,    _
    ]
])]

def is_key(key_event, key):
    return (hasattr(key_event.key, 'resolved_key') and key_event.key.resolved_key == key) or key_event.key == key

def before_resolved(key_event):
    if key_event.pressed and (is_key(key_event, ATAB) or is_key(key_event, CTAB)):
        if not keyboard.is_key_pressed(ACTMOD) and keyboard.is_key_pressed(MNAV):
            if is_key(key_event, ATAB):
                ACTMOD.mods = KC_LALT
                CTAB.mods = KC_LSFT
            else:
                ACTMOD.mods = KC_LCTL
                ATAB.mods = KC_LSFT
            keyboard.press_key(ACTMOD)

    if not key_event.pressed and key_event.key == MNAV:
        if keyboard.is_key_pressed(ACTMOD):
            ATAB.mods = 0
            CTAB.mods = 0
            keyboard.release_key(ACTMOD)

keyboard.before_resolved = before_resolved


was_caps_locked = False

def on_layer_changed(layer, prev_layer):
    global was_caps_locked
    if layer not in (BASE, LOCK):
        if keyboard.is_caps_locked():
            was_caps_locked = True
            keyboard.unlock_caps()
    else:
        if was_caps_locked:
            was_caps_locked = False
            keyboard.lock_caps()

keyboard.on_layer_changed = on_layer_changed

if ble_mode:
    def on_tick():
        if keyboard.hid.ble.connected:
            pixels[0] = (0, 1, 0, 0.05) # blue
        else:
            pixels[0] = (0, 0, 1, 0.05) # green

    keyboard.on_tick = on_tick
else:
    pixels[0] = (0, 1, 1, 0.05) # blue and green

print("Started")

if __name__ == '__main__':
    keyboard.go()


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