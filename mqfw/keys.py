from mqfw.hid import HIDReportTypes
from mqfw.time import now, time_diff
from mqfw.utils import find


# KC_NUMLOCK = 0x01
KC_CAPSLOCK = 0x02
# KC_SCROLLLOCK = 0x04
# KC_COMPOSE = 0x08
# KC_KANA = 0x10
# KC_RESERVED = 0x20

KC_LCTL = 0x01
KC_LSFT = 0x02
KC_LALT = 0x04
KC_LWIN = 0x08
KC_RCTL = 0x10
KC_RSFT = 0x20
KC_RALT = 0x40
KC_RWIN = 0x80

class HIDResults:
    def __init__(self, hid_type, keycode, mods, disable_mods):
        self.hid_usage = hid_type
        self.keycode = keycode
        self.mods = mods
        self.disable_mods = disable_mods


class KeyEvent:
    def __init__(self, int_coord, pressed):
        self.time = now()
        self.int_coord = int_coord
        self.pressed = pressed
        self.keyboard = None
        self.hid_results = None
        self.to_be_removed = False

    def prepare(self, keyboard):
        if self.keyboard:
            return
        self.keyboard = keyboard
        self.parent = find(reversed(keyboard.resolved_key_events), lambda i: i.int_coord == self.int_coord)
        self.key = self.parent.key if self.parent else keyboard.get_keymap_key(self.int_coord)
        print("prepared", self.key)

    def resolve(self):
        result = self.key.resolve(self, self.keyboard)
        if isinstance(result, HIDResults):
            self.hid_results = result
            return True
        return result
    
    def remove(self):
        self.to_be_removed = True

    def remove_all(self):
        if self.parent:
            self.parent.remove_all()
        self.remove()


class Key:
    def __init__(self, hid_type, keycode, mods=0, disable_mods=0):
        self.hid_type = hid_type
        self.keycode = keycode
        self.mods = mods
        self.disable_mods = disable_mods
        
    def __repr__(self):
        return '({},{},{})'.format(self.keycode, self.mods, self.disable_mods)

    def resolve(self, key_event, keyboard):
        if key_event.pressed:
            if self.hid_type and (self.keycode or self.mods > 0 or self.disable_mods > 0):
                return HIDResults(self.hid_type, self.keycode, self.mods, self.disable_mods)
        else:
            key_event.remove_all()
        return True


class KeyboardKey(Key):
    def __init__(self, keycode, mods=0, disable_mods=0):
        super().__init__(HIDReportTypes.KEYBOARD, keycode, mods, disable_mods)


# class ConsumerKey(Key):
#     def __init__(self, keycode):
#         super().__init__(HIDReportTypes.CONSUMER, keycode)


class MouseKey(Key):
    def __init__(self, button):
        super().__init__(HIDReportTypes.MOUSE, button)


class HoldTapKey(Key):
    def __init__(self, tapping_term=None):
        super().__init__(None, None, 0, 0)
        self.tapping_term = tapping_term

    def resolve(self, key_event, keyboard):
        # balanced flavour:
        #   key is resolved if 
        #     1) tapping term expires (resolves to hold)
        #     2) key is released within tapping term (resolves to tap)
        #     3) or another key is pressed and released within tapping 
        #        term and before this key is released (resolves to hold)
        if key_event.pressed:
            # 1)
            if self._tapping_term_expired(key_event, keyboard):
                return self._resolve_hold(key_event, keyboard)
            # 2)
            elif self._key_released(key_event, keyboard):
                return self._resolve_tap(key_event, keyboard)
            # 3)
            elif self._other_key_tapped(key_event, keyboard):
                return self._resolve_hold(key_event, keyboard)
            return False
        else:
            return self._resolve_release(key_event, keyboard)

    def get_tapping_term(self, keyboard):
        if self.tapping_term is not None:
            return self.tapping_term
        return keyboard.tapping_term

    def _tapping_term_expired(self, key_event, keyboard):
        return time_diff(now(), key_event.time) >= self.get_tapping_term(keyboard)

    def _key_released(self, key_event, keyboard):
        events = keyboard.unresolved_key_events[1:]
        for i, u in enumerate(events):
            if not u.pressed and u.int_coord == key_event.int_coord:
                return True
        return False

    def _other_key_tapped(self, key_event, keyboard):
        events = keyboard.unresolved_key_events[1:]
        for i, p in enumerate(events):
            if p.pressed:
                for u in events[i + 1:]:
                    if not u.pressed and u.int_coord == p.int_coord:
                        return True
        return False

    def _resolve_hold(self, key_event, keyboard):
        return True

    def _resolve_tap(self, key_event, keyboard):
        return True

    def _resolve_release(self, key_event, keyboard):
        key_event.remove_all()
        return True


class ModTapKey(HoldTapKey):
    def __init__(self, mod_key, tap_key, tapping_term=None):
        super().__init__(tapping_term)
        self.mod_key = mod_key
        self.tap_key = tap_key
        self.resolved_key = None

    def _resolve_hold(self, key_event, keyboard):
        self.resolved_key = self.mod_key
        return self.resolved_key.resolve(key_event, keyboard)

    def _resolve_tap(self, key_event, keyboard):
        self.resolved_key = self.tap_key
        return self.resolved_key.resolve(key_event, keyboard)

    def _resolve_release(self, key_event, keyboard):
        if self.resolved_key:
            return self.resolved_key.resolve(key_event, keyboard)
        else:
            key_event.remove_all()
            return True


class ModTapKey(HoldTapKey):
    def __init__(self, mod_key, tap_key, tapping_term=None):
        super().__init__(tapping_term)
        self.mod_key = mod_key
        self.tap_key = tap_key
        self.resolved_key = None

    def _resolve_hold(self, key_event, keyboard):
        self.resolved_key = self.mod_key
        return self.resolved_key.resolve(key_event, keyboard)

    def _resolve_tap(self, key_event, keyboard):
        self.resolved_key = self.tap_key
        return self.resolved_key.resolve(key_event, keyboard)

    def _resolve_release(self, key_event, keyboard):
        if self.resolved_key:
            return self.resolved_key.resolve(key_event, keyboard)
        else:
            key_event.remove_all()
            return True


class LayerTapKey(HoldTapKey):
    def __init__(self, layer, tap_key, tapping_term=None):
        super().__init__(tapping_term)
        self.layer = layer
        self.tap_key = tap_key
        self.resolved_to = None

    def _resolve_hold(self, key_event, keyboard):
        self.resolved_to = self.layer
        keyboard.activate_layer(self.layer)
        return True

    def _resolve_tap(self, key_event, keyboard):
        self.resolved_to = self.tap_key
        return self.tap_key.resolve(key_event, keyboard)

    def _resolve_release(self, key_event, keyboard):
        if isinstance(self.resolved_to, Key):
            return self.resolved_to.resolve(key_event, keyboard)
        elif isinstance(self.resolved_to, int):
            keyboard.deactivate_layer(self.layer)
            key_event.remove_all()
            return True
        else:
            key_event.remove_all()
            return True


class MomentaryLayerKey(Key):
    def __init__(self, layer):
        super().__init__(None, None, 0, 0)
        self.layer = layer

    def resolve(self, key_event, keyboard):
        if key_event.pressed:
            keyboard.activate_layer(self.layer)
        else:
            keyboard.deactivate_layer(self.layer)
            key_event.remove_all()
        return True


class ShiftOverrideKey(Key):
    def __init__(self, base_key, shifted_key, ignore_caps=False):
        super().__init__(None, None, 0, 0)
        self.base_key = base_key
        self.shifted_key = shifted_key
        self.resolved_key = None
        self.ignore_caps = ignore_caps

    def resolve(self, key_event, keyboard):
        if self.ignore_caps:
            is_shifted = keyboard.is_shift_pressed()
        else:
            is_shifted = keyboard.is_shifted()

        if key_event.pressed:
            if is_shifted:
                return self._resolve_shifted(key_event, keyboard)
            else:
                return self._resolve_base(key_event, keyboard)
        else:
            return self._resolve_release(key_event, keyboard)

    def _resolve_base(self, key_event, keyboard):
        self.resolved_key = self.base_key
        result = self.resolved_key.resolve(key_event, keyboard)
        self._handle_caps(result, keyboard)
        return result

    def _resolve_shifted(self, key_event, keyboard):
        self.resolved_key = self.shifted_key
        result = self.resolved_key.resolve(key_event, keyboard)
        self._handle_caps(result, keyboard)
        return result

    def _handle_caps(self, resolve_result, keyboard):
        if isinstance(resolve_result, HIDResults):
            is_shifted_key = (resolve_result.mods & (KC_LSFT | KC_RSFT)) > 0
            is_caps_locked = keyboard.is_caps_locked()
            print(is_shifted_key, is_caps_locked)
            if (is_shifted_key == is_caps_locked) or (not is_shifted_key and self.ignore_caps):
                resolve_result.disable_mods |= KC_LSFT | KC_RSFT
            elif not is_shifted_key and is_caps_locked:
                resolve_result.mods |= KC_LSFT

    def _resolve_release(self, key_event, keyboard):
        if self.resolved_key:
            return self.resolved_key.resolve(key_event, keyboard)
        else:
            key_event.remove_all()
            return True
