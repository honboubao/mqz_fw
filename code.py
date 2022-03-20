print("Starting")

import board
import adafruit_dotstar

pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
pixels[0] = (0, 0, 1, 0.05)

from mqfw.keycodes import *
from mqfw.keys import Key, KeyboardKey
from mqfw.keyboard import Keyboard
from mqfw.matrix import DiodeOrientation

keyboard = Keyboard()
keyboard.ble_name = 'Micro Qwertz BLE'
keyboard.debug_enabled = True

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
        ____, ____, FN,   ____, ____, ____, ____, ____, ____, ____,
        LSFT, SYM,  NUM,  ____, ____, LOCK, ____, NUM,  SYM,  RSFT,
        LCTL, LWIN, LALT, ____, ____, FN,   ____, RALT, RWIN, RCTL,
        _,    _,    _,    _,    ____, ____, _,    _,    _,    _
    ]
keyboard.keymap = [apply_modtaps(keymap, layer) for layer, keymap in enumerate([
    [ # base
        Q,    W,    E,    R,    T,    Z,    U,    I,    O,    P,
        A,    S,    D,    F,    G,    H,    J,    K,    L,    Ö,
        Y,    X,    C,    V,    B,    N,    M,    Ü,    DTSS, Ä,
        _,    _,    _,    _,    MNAV, SPC,  _,    _,    _,    _
    ],
    [ # num
        DEG,  SECT, SUP2, SUP3, ____, COLN, N7,   N8,   N9,   BKSP,
        EURO, ACUT, MICR, SPC,  ____, COMM, N4,   N5,   N6,   ENT,
        ____, BSLS, ____, ____, ____, DOT,  N1,   N2,   N3,   MINS,
        _,    _,    _,    _,    MNAV, N0,   _,    _,    _,    _
    ],
    [ # sym
        CIRC, DLR,  HASH, PERC, AMPR, PIPE, LCBR, RCBR, LBRC, RBRC,
        AT,   GRV,  QUOT, DQUO, QUES, EXLM, LPRN, RPRN, LABK, RABK,
        TILD, SLSH, ASTR, PLUS, MINS, EQL,  SCLN, COMM, COLN, UNDS,
        _,    _,    _,    _,    MNAV, SPC,  _,    _,    _,    _
    ],
    [ # fn
        ____, ____, ____, ____, INS,  SLCK, F7,   F8,   F9,   F10,
        LSFT, ____, ____, ____, PSCR, PAUS, F4,   F5,   F6,   F11,
        LCTL, LWIN, LALT, ____, APP,  ____, F1,   F2,   F3,   F12,
        _,    _,    _,    _,    MNAV, SPC,  _,    _,    _,    _
    ],
    [ # nav
        UNDO, HOME, UP,   END,  TAB,  PGUP, HOME, UP,   END,  BSDL,
        ESC,  LEFT, DOWN, RGHT, ENT,  PGDN, LEFT, DOWN, RGHT, ENT,
        MBBK, MBFW, BKSP, DEL,  ATAB, CTAB, CUT,  COPY, PAST, ESC,
        _,    _,    _,    _,    MNAV, TAB,  _,    _,    _,    _
    ],
    [ # lock
        ____, ____, LFN,  ____, ____, ____, ____, ____, ____, ____,
        CAPS, LSYM, LNUM, ____, ____, ____, ____, LNUM, LSYM, CAPS,
        ____, ____, ____, ____, ____, ____, ____, ____, ____, ____,
        _,    _,    _,    _,    LNAV, CLLK, _,    _,    _,    _
    ]
])]

def before_resolved(key_event):
    if key_event.pressed and (key_event.key == ATAB or key_event.key == CTAB):
        if not keyboard.is_key_pressed(ACTMOD) and keyboard.is_key_pressed(MNAV):
            ACTMOD.mods = KC_LALT if key_event.key == ATAB else KC_LCTL
            keyboard.press_key(ACTMOD)

    if not key_event.pressed and key_event.key == MNAV:
        if keyboard.is_key_pressed(ACTMOD):
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


pixels[0] = (0, 1, 0, 0.05)

print("Started")

if __name__ == '__main__':
    keyboard.go()


# TODO
# (ZMKK hold tap flavors)
# Mouse buttons 4/5
# hide circuitpy drive
# bluetooth multiple connections
# ble status light
# double tap repeat
# ble powersaving
# ble and usb