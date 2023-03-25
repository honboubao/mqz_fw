from mqzfw.hid import HIDReportTypes
from mqzfw.time import now, time_diff
from mqzfw.utils import find


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
        self.hid_type = hid_type
        self.keycode = keycode
        self.mods = mods
        self.disable_mods = disable_mods

    def __repr__(self):
        return '<{}: keycode={}, mods={:08b}, disable_mods={:08b}, hid_type={}>'.format(
            self.__class__.__name__, self.keycode, self.mods, self.disable_mods, self.hid_type)


class KeyEvent:
    def __init__(self, int_coord, pressed):
        self.time = now()
        self.int_coord = int_coord
        self.pressed = pressed
        self.keyboard = None
        self.hid_results = None
        self.to_be_removed = False
        self.parent = None
        self.key = None

    @classmethod
    def virtual(cls, keyboard, key, pressed):
        key_event = cls(None, pressed)
        key_event.keyboard = keyboard
        key_event.key = key
        if not pressed:
            key_event.parent = find(reversed(keyboard.resolved_key_events), lambda i: i.int_coord is None and i.key == key)
        if not key_event.resolve():
            raise Exception("Can't create virtual key event from key that doesn't resolve immediately")
        return key_event

    def __repr__(self):
        return '<{}: int_coord={}, pressed={}, to_be_removed={}, hid_results={}, key={}, parent={}>'.format(
            self.__class__.__name__, self.int_coord, self.pressed, self.to_be_removed, self.hid_results, self.key, self.parent)

    def prepare(self, keyboard):
        if self.keyboard:
            return
        self.keyboard = keyboard
        self.parent = find(reversed(keyboard.resolved_key_events), lambda i: i.int_coord == self.int_coord)
        self.key = self.parent.key if self.parent else keyboard.get_keymap_key(self.int_coord)

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
        return '<{}: keycode={}, mods={:08b}, disable_mods={:08b}>'.format(
            self.__class__.__name__, self.keycode, self.mods, self.disable_mods)

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
        self.previous_tap_time = None

    def resolve(self, key_event, keyboard):
        # balanced flavour:
        #   key is resolved if 
        #     1) another key is pressed and released within tapping
        #        term and before this key is released (resolves to hold)
        #     2) key is released within tapping term (resolves to tap)
        #     3) tapping term expires
        #        3a) resolve to tap for tap-tap-hold action
        #        3b) resolve to hold
        if key_event.pressed:
            # 1)
            if self._is_other_key_tapped_within_tapping_term(key_event, keyboard):
                self.previous_tap_time = None
                return self._resolve_hold(key_event, keyboard)
            # 2)
            elif self._is_key_released_within_tapping_term(key_event, keyboard):
                self.previous_tap_time = key_event.time
                return self._resolve_tap(key_event, keyboard)
            # 3)
            elif not self._is_within_tapping_term(now(), key_event, keyboard):
                # 3a)
                if self._is_double_tap(key_event, keyboard):
                    self.previous_tap_time = key_event.time
                    return self._resolve_tap(key_event, keyboard)
                # 3b)
                else:
                    self.previous_tap_time = None
                    return self._resolve_hold(key_event, keyboard)
            return False
        else:
            return self._resolve_release(key_event, keyboard)

    def get_tapping_term(self, keyboard):
        if self.tapping_term is not None:
            return self.tapping_term
        return keyboard.tapping_term

    def _is_within_tapping_term(self, time, key_event, keyboard):
        return time_diff(time, key_event.time) <= self.get_tapping_term(keyboard)

    def _is_double_tap(self, key_event, keyboard):
        return self.previous_tap_time is not None and time_diff(key_event.time, self.previous_tap_time) <= self.get_tapping_term(keyboard)

    def _is_key_released_within_tapping_term(self, key_event, keyboard, key_index=0):
        p = keyboard.unresolved_key_events[key_index]
        events = keyboard.unresolved_key_events[key_index + 1:]
        for u in events:
            if not u.pressed and u.int_coord == p.int_coord:
                return self._is_within_tapping_term(u.time, key_event, keyboard)
        return False

    def _is_other_key_tapped_within_tapping_term(self, key_event, keyboard):
        events = keyboard.unresolved_key_events[1:]
        for i, p in enumerate(events):
            if p.pressed and self._is_key_released_within_tapping_term(key_event, keyboard, i + 1):
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

    def __repr__(self):
        return '<{}: mod_key={}, tap_key={}, resolved_key={}>'.format(
            self.__class__.__name__, self.mod_key, self.tap_key, self.resolved_key)

    def _resolve_hold(self, key_event, keyboard):
        self.resolved_key = self.mod_key
        return self.resolved_key.resolve(key_event, keyboard)

    def _resolve_tap(self, key_event, keyboard):
        self.resolved_key = self.tap_key
        return self.resolved_key.resolve(key_event, keyboard)

    def _resolve_release(self, key_event, keyboard):
        if self.resolved_key:
            result = self.resolved_key.resolve(key_event, keyboard)
            if result:
                self.resolved_key = None
            return result
        else:
            self.resolved_key = None
            key_event.remove_all()
            return True


class LayerTapKey(HoldTapKey):
    def __init__(self, layer, tap_key, tapping_term=None):
        super().__init__(tapping_term)
        self.layer = layer
        self.tap_key = tap_key
        self.resolved_to = None

    def __repr__(self):
        return '<{}: layer={}, tap_key={}, resolved_to={}>'.format(
            self.__class__.__name__, self.layer, self.tap_key, self.resolved_to)

    def _resolve_hold(self, key_event, keyboard):
        self.resolved_to = self.layer
        keyboard.activate_layer(self.layer)
        return True

    def _resolve_tap(self, key_event, keyboard):
        self.resolved_to = self.tap_key
        return self.tap_key.resolve(key_event, keyboard)

    def _resolve_release(self, key_event, keyboard):
        if isinstance(self.resolved_to, Key):
            result = self.resolved_to.resolve(key_event, keyboard)
            if result:
                self.resolved_to = None
            return result
        elif isinstance(self.resolved_to, int):
            keyboard.deactivate_layer(self.resolved_to)
            self.resolved_to = None
            key_event.remove_all()
            return True
        else:
            self.resolved_to = None
            key_event.remove_all()
            return True


class MomentaryLayerKey(Key):
    def __init__(self, layer):
        super().__init__(None, None, 0, 0)
        self.layer = layer

    def __repr__(self):
        return '<{}: layer={}>'.format(self.__class__.__name__, self.layer)

    def resolve(self, key_event, keyboard):
        if key_event.pressed:
            keyboard.activate_layer(self.layer)
        else:
            keyboard.deactivate_layer(self.layer)
            key_event.remove_all()
        return True


class SetLayerKey(Key):
    def __init__(self, layer):
        super().__init__(None, None, 0, 0)
        self.layer = layer

    def __repr__(self):
        return '<{}: layer={}>'.format(self.__class__.__name__, self.layer)

    def resolve(self, key_event, keyboard):
        if key_event.pressed:
            keyboard.activate_layer(self.layer)
        else:
            key_event.remove_all()
        return True


class ClearLockKey(Key):
    def __init__(self):
        super().__init__(None, None, 0, 0)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def resolve(self, key_event, keyboard):
        if key_event.pressed:
            keyboard.set_layer(0)
            keyboard.unlock_caps()
        else:
            key_event.remove_all()
        return True


class ShiftOverrideKey(Key):
    def __init__(self, base_key, shifted_key, ignore_caps=False):
        super().__init__(None, None, 0, 0)
        self.base_key = base_key
        self.shifted_key = shifted_key
        self.resolved_key = None
        self.ignore_caps = ignore_caps

    def __repr__(self):
        return '<{}: base_key={}, shifted_key={}, ignore_caps={}, resolved_key={}>'.format(
            self.__class__.__name__, self.base_key, self.shifted_key, self.ignore_caps, self.resolved_key)

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
