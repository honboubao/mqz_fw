from mqfw.keys import KC_LALT, KC_LCTL, KC_LSFT, KC_LWIN, KC_RALT, KC_RCTL, KC_RSFT, KC_RWIN, Key, KeyboardKey, LayerTapKey, ModTapKey, MouseKey, ShiftOverrideKey

XXXX = ____ = NOOP = Key(None, None, 0, 0)
MT = ModTapKey
LT = LayerTapKey
SO = ShiftOverrideKey


# ┌───┐   ┌───┬───┬───┬───┐ ┌───┬───┬───┬───┐ ┌───┬───┬───┬───┐
# │ESC│   │F1 │F2 │F3 │F4 | |F5 |F6 |F7 |F8 │ |F9 |F10|F11|F12│
# └───┘   └───┴───┴───┴───┘ └───┴───┴───┴───┘ └───┴───┴───┴───┘
# ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐
# │   │   │   │   │   │   │   │   │   │   │   │   │   │  BKSP │
# ├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤
# │ TAB │   │   │   │   │   │   │   │   │   │   │   │   │ ENT │
# ├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┐    │
# │ CAPS │   │   │   │   │   │   │   │   │   │   │   │   │    │
# ├────┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┴────┤
# │LSFT│   │   │   │   │   │   │   │   │   │   │   │    RSFT  │
# ├────┼───┴┬──┴─┬─┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬────┤
# │LCTL│LWIN│LALT│           SPC          │RALT│RWIN│APP │RCTL│
# └────┴────┴────┴────────────────────────┴────┴────┴────┴────┘
LCTL = KeyboardKey(None, KC_LCTL)
LSFT = KeyboardKey(None, KC_LSFT)
LALT = KeyboardKey(None, KC_LALT)
LWIN = KeyboardKey(None, KC_LWIN)
RCTL = KeyboardKey(None, KC_RCTL)
RSFT = KeyboardKey(None, KC_RSFT)
RALT = KeyboardKey(None, KC_RALT)
RWIN = KeyboardKey(None, KC_RWIN)

ENT = KeyboardKey(40)
ESC = KeyboardKey(41)
BKSP = KeyboardKey(42)
TAB = KeyboardKey(43)
SPC = KeyboardKey(44)
CAPS = KeyboardKey(57)
APP = KeyboardKey(101)

F1 = KeyboardKey(58)
F2 = KeyboardKey(59)
F3 = KeyboardKey(60)
F4 = KeyboardKey(61)
F5 = KeyboardKey(62)
F6 = KeyboardKey(63)
F7 = KeyboardKey(64)
F8 = KeyboardKey(65)
F9 = KeyboardKey(66)
F10 = KeyboardKey(67)
F11 = KeyboardKey(68)
F12 = KeyboardKey(69)

# ┌────┬────┬────┐
# │PSCR│SLCK|PAUS│
# └────┴────┴────┘
# ┌────┬────┬────┐  ┌────┬────┬────┬────┐
# │INS │HOME│PGUP|  │NLCK|PSLS|PAST│PMNS│
# ├────┼────┼────┤  ├────┼────┼────┤────┤
# │DEL │END │PGDN│  | P7 | P8 | P9 |    |
# └────┴────┴────┘  |────┤────┤────┤PPLS|
#                   | P4 | P5 | P6 |    |
#      ┌────┐       |────┤────┤────┤────┤
#      | UP |       | P1 | P2 | P3 |    |
# ┌────┤────┤────┐  |────┴────┤────┤PENT|
# |LEFT|DOWN|RGHT|  |    P0   |PDOT|    | 
# └────┴────┴────┘  └─────────┴────┴────┘
PSCR = KeyboardKey(70)
SLCK = KeyboardKey(71)
PAUS = KeyboardKey(72)

INS = KeyboardKey(73)
HOME = KeyboardKey(74)
PGUP = KeyboardKey(75)
DEL = KeyboardKey(76)
END = KeyboardKey(77)
PGDN = KeyboardKey(78)

RGHT = KeyboardKey(79)
LEFT = KeyboardKey(80)
DOWN = KeyboardKey(81)
UP = KeyboardKey(82)

# NLCK = KeyboardKey(83)
# PSLS = KeyboardKey(84)
# PAST = KeyboardKey(85)
# PMNS = KeyboardKey(86)
# PPLS = KeyboardKey(87)
# PENT = KeyboardKey(88)
# P1 = KeyboardKey(89)
# P2 = KeyboardKey(90)
# P3 = KeyboardKey(91)
# P4 = KeyboardKey(92)
# P5 = KeyboardKey(93)
# P6 = KeyboardKey(94)
# P7 = KeyboardKey(95)
# P8 = KeyboardKey(96)
# P9 = KeyboardKey(97)
# P0 = KeyboardKey(98)
# PDOT = KeyboardKey(99)
# PEQL = KeyboardKey(103)
# PCMM = KeyboardKey(133)


# ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐
# │ ^ │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ 0 │ ß │ ´ │       │
# ├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤
# │     │ Q │ W │ E │ R │ T │ Z │ U │ I │ O │ P │ Ü │ + │     │
# ├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┐    │
# │      │ A │ S │ D │ F │ G │ H │ J │ K │ L │ Ö │ Ä │ # │    │
# ├────┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┴────┤
# │    │ < │ Y │ X │ C │ V │ B │ N │ M │ , │ . │ - │          │
# ├────┼───┴┬──┴─┬─┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬────┤
# │    │    │    │                        │    │    │    │    │
# └────┴────┴────┴────────────────────────┴────┴────┴────┴────┘
# Row 1
CIRC = KeyboardKey(53)         # ^ (dead)
N1 = KeyboardKey(30)           # 1
N2 = KeyboardKey(31)           # 2
N3 = KeyboardKey(32)           # 3
N4 = KeyboardKey(33)           # 4
N5 = KeyboardKey(34)           # 5
N6 = KeyboardKey(35)           # 6
N7 = KeyboardKey(36)           # 7
N8 = KeyboardKey(37)           # 8
N9 = KeyboardKey(38)           # 9
N0 = KeyboardKey(39)           # 0
ß = KeyboardKey(45)           # ß
ACUT = KeyboardKey(46)         # ´ (dead)
# Row 2
Q = KeyboardKey(20)            # Q
W = KeyboardKey(26)            # W
E = KeyboardKey(8)             # E
R = KeyboardKey(21)            # R
T = KeyboardKey(23)            # T
Z = KeyboardKey(28)            # Z
U = KeyboardKey(24)            # U
I = KeyboardKey(12)            # I
O = KeyboardKey(18)            # O
P = KeyboardKey(19)            # P
Ü = KeyboardKey(47)            # Ü
PLUS = KeyboardKey(48)         # +
# Row 3
A = KeyboardKey(4)             # A
S = KeyboardKey(22)            # S
D = KeyboardKey(7)             # D
F = KeyboardKey(9)             # F
G = KeyboardKey(10)            # G
H = KeyboardKey(11)            # H
J = KeyboardKey(13)            # J
K = KeyboardKey(14)            # K
L = KeyboardKey(15)            # L
Ö = KeyboardKey(51)            # Ö
Ä = KeyboardKey(52)            # Ä
HASH = KeyboardKey(50)         # #
# Row 4
LABK = KeyboardKey(100)        # <
Y = KeyboardKey(29)            # Y
X = KeyboardKey(27)            # X
C = KeyboardKey(6)             # C
V = KeyboardKey(25)            # V
B = KeyboardKey(5)             # B
N = KeyboardKey(17)            # N
M = KeyboardKey(16)            # M
COMM = KeyboardKey(54)         # ,
DOT = KeyboardKey(55)          # .
MINS = KeyboardKey(56)         # -

# Shifted symbols
# ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐
# │ ° │ ! │ " │ § │ $ │ % │ & │ / │ ( │ ) │ = │ ? │ ` │       │
# ├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤
# │     │   │   │   │   │   │   │   │   │   │   │   │ * │     │
# ├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┐    │
# │      │   │   │   │   │   │   │   │   │   │   │   │ ' │    │
# ├────┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┴────┤
# │    │ > │   │   │   │   │   │   │   │ ; │ : │ _ │          │
# ├────┼───┴┬──┴─┬─┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬────┤
# │    │    │    │                        │    │    │    │    │
# └────┴────┴────┴────────────────────────┴────┴────┴────┴────┘
# Row 1
DEG = KeyboardKey(CIRC.keycode, KC_LSFT)         # °
EXLM = KeyboardKey(N1.keycode, KC_LSFT)          # !
DQUO = KeyboardKey(N2.keycode, KC_LSFT)          # "
SECT = KeyboardKey(N3.keycode, KC_LSFT)          # §
DLR = KeyboardKey(N4.keycode, KC_LSFT)           # $
PERC = KeyboardKey(N5.keycode, KC_LSFT)          # %
AMPR = KeyboardKey(N6.keycode, KC_LSFT)          # &
SLSH = KeyboardKey(N7.keycode, KC_LSFT)          # /
LPRN = KeyboardKey(N8.keycode, KC_LSFT)          # (
RPRN = KeyboardKey(N9.keycode, KC_LSFT)          # )
EQL = KeyboardKey(N0.keycode, KC_LSFT)           # =
QUES = KeyboardKey(ß.keycode, KC_LSFT)           # ?
GRV = KeyboardKey(ACUT.keycode, KC_LSFT)         # ` (dead)
# Row 2
ASTR = KeyboardKey(PLUS.keycode, KC_LSFT)        # *
# Row 3
QUOT = KeyboardKey(HASH.keycode, KC_LSFT)        # '
# Row 4
RABK = KeyboardKey(LABK.keycode, KC_LSFT)        # >
SCLN = KeyboardKey(COMM.keycode, KC_LSFT)        # ;
COLN = KeyboardKey(DOT.keycode, KC_LSFT)         # :
UNDS = KeyboardKey(MINS.keycode, KC_LSFT)        # _

# AltGr symbols
# ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐
# │   │   │ ² │ ³ │   │   │   │ { │ [ │ ] │ } │ \ │   │       │
# ├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤
# │     │ @ │   │ € │   │   │   │   │   │   │   │   │ ~ │     │
# ├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┐    │
# │      │   │   │   │   │   │   │   │   │   │   │   │   │    │
# ├────┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┴────┤
# │    │ | │   │   │   │   │   │   │ µ │   │   │   │          │
# ├────┼───┴┬──┴─┬─┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬────┤
# │    │    │    │                        │    │    │    │    │
# └────┴────┴────┴────────────────────────┴────┴────┴────┴────┘
# Row 1
SUP2 = KeyboardKey(N2.keycode, KC_RALT)     # ²
SUP3 = KeyboardKey(N3.keycode, KC_RALT)     # ³
LCBR = KeyboardKey(N7.keycode, KC_RALT)     # {
LBRC = KeyboardKey(N8.keycode, KC_RALT)     # [
RBRC = KeyboardKey(N9.keycode, KC_RALT)     # ]
RCBR = KeyboardKey(N0.keycode, KC_RALT)     # }
BSLS = KeyboardKey(ß.keycode, KC_RALT)      # \
# Row 2
AT = KeyboardKey(Q.keycode, KC_RALT)        # @
EURO = KeyboardKey(E.keycode, KC_RALT)      # €
TILD = KeyboardKey(RBRC.keycode, KC_RALT)   # ~
# Row 4
PIPE = KeyboardKey(LABK.keycode, KC_RALT)   # |
MICR = KeyboardKey(M.keycode, KC_RALT)      # µ


# Media Keys
# AUDIO_MUTE = MUTE = ConsumerKey(226)  # 0xE2
# AUDIO_VOL_UP = VOLU = ConsumerKey(233)  # 0xE9
# AUDIO_VOL_DOWN = VOLD = ConsumerKey(234)  # 0xEA
# MEDIA_NEXT_TRACK = MNXT = ConsumerKey(181)  # 0xB5
# MEDIA_PREV_TRACK = MPRV = ConsumerKey(182)  # 0xB6
# MEDIA_STOP = MSTP = ConsumerKey(183)  # 0xB7
# MEDIA_PLAY_PAUSE = MPLY = ConsumerKey(205)  # 0xCD (this may not be right)
# MEDIA_EJECT = EJCT = ConsumerKey(184)  # 0xB8
# MEDIA_FAST_FORWARD = MFFD = ConsumerKey(179)  # 0xB3
# MEDIA_REWIND = MRWD = ConsumerKey(180)  # 0xB4

# Mouse Buttons
# MOUSE_BUTTON_LEFT = MB1 = MBL = MouseKey(1)
# MOUSE_BUTTON_RIGHT = MB2 = MBR = MouseKey(2)
# MOUSE_BUTTON_MIDDLE = MB3 = MBM = MouseKey(4)
MOUSE_BUTTON_BACK = MB4 = MBBK = MouseKey(8)
MOUSE_BUTTON_FORWARD = MB5 = MBFW = MouseKey(16)