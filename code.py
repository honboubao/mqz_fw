print("Starting")

import board
import adafruit_dotstar

pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
pixels[0] = (0, 0, 1, 0.05)

from mqfw.keycodes import *
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

_ = ____
BASE = 0
NUM = 1
SYM = 2
FN = 3
NAV = 4
LOCK = 5

UNDO = LCTL(Z)
CUT = LCTL(X)
COPY = LCTL(C)
PAST = LCTL(V)
TNAV = TT(NAV)
DTSS = SO(DOT, ß)
BSDL = SO(BKSP, DEL)


def transform_modkey(key, mod):
    if key.key in (LSFT, LCTL, LWIN, LALT):
        return key

    if isinstance(mod, mod.mods > 0):
        return MT(mod, key)
    if isinstance(mod, int):
        return LT(mod, key)
    return key

def apply_modtaps(keymap):
    return [transform_modkey(key, mod) for key, mod in zip(keymap, modtaps)]

modtaps = [ # mod taps
        ____, ____, FN,   ____, ____, ____, ____, FN,   ____, ____,
        LSFT, SYM,  NUM,  ____, ____, LOCK, ____, NUM,  SYM,  RSFT,
        LCTL, LWIN, LALT, ____, ____, ____, ____, RALT, RWIN, RCTL,
        _,    _,    _,    _,    ____, ____, _,    _,    _,    _   
    ]
keyboard.keymap = [apply_modtaps(keymap) for keymap in [
    [ # base
        Q,    W,    E,    R,    T,    Z,    U,    I,    O,    P,
        A,    S,    D,    F,    G,    H,    J,    K,    L,    Ö,
        Y,    X,    C,    V,    B,    N,    M,    Ü,    DTSS, Ä,
        _,    _,    _,    _,    TNAV, SPC,  _,    _,    _,    _   
    ],
    [ # num
        DEG,  SECT, SUP2, SUP3, ____, COLN, N7,   N8,   N9,   BKSP,
        EURO, ACUT, MICR, SPC,  ____, COMM, N4,   N5,   N6,   ENT,
        ____, BSLS, ____, ____, ____, DOT,  N1,   N2,   N3,   MINS,
        _,    _,    _,    _,    TNAV, N0,   _,    _,    _,    _   
    ],
    [ # sym
        CIRC, DLR,  HASH, PERC, AMPR, PIPE, LCBR, RCBR, LBRC, RBRC,
        AT,   GRV,  QUOT, DQUO, QUES, EXLM, LPRN, RPRN, LABK, RABK,
        TILD, SLSH, ASTR, PLUS, MINS, EQL,  SCLN, COMM, COLN, UNDS,
        _,    _,    _,    _,    TNAV, SPC,  _,    _,    _,    _   
    ],
    [ # fn
        ____, ____, ____, ____, INS,  SLCK, F7,   F8,   F9,   F10,
        LSFT, ____, ____, ____, PSCR, PAUS, F4,   F5,   F6,   F11,
        LCTL, LWIN, LALT, ____, APP,  ____, F1,   F2,   F3,   F12,
        _,    _,    _,    _,    TNAV, SPC,  _,    _,    _,    _   
    ],
    [ # nav
        ____, HOME, UP,   END,  TAB,  PGUP, HOME, UP,   END,  BSDL,
        ____, LEFT, DOWN, RGHT, ENT,  PGDN, LEFT, DOWN, RGHT, ENT,
        UNDO, ESC,  BKSP, DEL,  MBBK, MBFW, CUT,  COPY, PAST, ESC,
        _,    _,    _,    _,    TNAV, TAB,  _,    _,    _,    _   
    ],
    [ # lock
        ____, ____, ____, ____, ____, ____, ____, ____, ____, ____,
        CAPS, ____, ____, ____, ____, ____, ____, ____, ____, CAPS,
        ____, ____, ____, ____, ____, ____, ____, ____, ____, ____,
        _,    _,    _,    _,    ____, ____,  _,    _,    _,    _   
    ]
]]


pixels[0] = (0, 1, 0, 0.05)

if __name__ == '__main__':
    keyboard.go()


# TODO
# (ZMKK hold tap flavors)
# Mouse buttons 4/5
# shift dot eszett
# lock/clear lock

# alt tab
#     shift backspace delete

# deactivate caps on layer change

# hide circuitpy drive

# repeat arrow keys

# bluetooth multiple connections
# ble status light

# double tap repeat

# ble powersaving

# ble and usb