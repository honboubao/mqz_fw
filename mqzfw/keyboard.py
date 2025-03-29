from asyncio import sleep
from mqzfw.hid import USBHID
from mqzfw.keys import KC_CAPSLOCK, KC_LCTL, KC_LSFT, KC_RCTL, KC_RSFT, KeyEvent
from misc.utils import find
from misc.logging import debug
import mqzfw.keycodes as KC

class Keyboard:
    debug_enabled = False

    # config
    keymap = []
    holdtaps = []
    hid = None
    tapping_term = 300

    before_resolved = None
    on_layer_changed = None
    on_tick = None

    # state
    unresolved_key_events = []
    resolved_key_events = []

    _mods_active = set()
    _active_layers = [0]

    _hid_host_report_mods = 0x00

    async def run(self):
        while True:
            await self._main_loop()
            await sleep(0)

    # prev_hid_string = ''

    async def _main_loop(self):
        # hid_string = self.hid.__repr__()
        # if self.prev_hid_string != hid_string:
        #     print(hid_string)
        #     self.prev_hid_string = hid_string

        if self.on_tick is not None:
            self.on_tick()

        hid_host_report = self.hid.get_host_report()
        if hid_host_report and hid_host_report[0] != self._hid_host_report_mods:
            self._hid_host_report_mods = hid_host_report[0]

        if self.unresolved_key_events:
            e = self.unresolved_key_events[0]
            e.prepare(self)
            if await e.resolve():
                if self.before_resolved:
                    await self.before_resolved(e)
                self.resolved_key_events.append(e)
                self.unresolved_key_events.remove(e)
                debug('ResolvedKeyEvents({})', self.resolved_key_events)
            self.resolved_key_events = [e for e in self.resolved_key_events if not e.to_be_removed]

            await self._send_hid()

    async def _send_hid(self):
        self.hid.create_report(self.resolved_key_events)
        await self.hid.send()

    def add_matrix_key_event(self, matrix_key_event):
        self.unresolved_key_events.append(matrix_key_event)

    def get_keymap_key(self, int_coord):
        layer = self._active_layers[0]
        try:
            layer_key = self.keymap[layer][int_coord]
        except IndexError:
            layer_key = None
            debug('KeymapIndexError(int_coord={}, layer={layer})', int_coord, layer)
        debug('KeyResolution(key={}, int_coord={}, layer={})', layer_key, int_coord, layer)

        return layer_key

    async def _check_layer_changed(self, prev_layer):
        if self.on_layer_changed and self._active_layers[0] != prev_layer:
            await self.on_layer_changed(self._active_layers[0], prev_layer)

    async def set_layer(self, layer):
        prev_layer = self._active_layers[0]
        self._active_layers.clear()
        self._active_layers.append(layer)
        await self._check_layer_changed(prev_layer)

    async def activate_layer(self, layer):
        prev_layer = self._active_layers[0]
        self._active_layers.insert(0, layer)
        await self._check_layer_changed(prev_layer)

    async def deactivate_layer(self, layer):
        prev_layer = self._active_layers[0]
        if layer in self._active_layers:
            self._active_layers.remove(layer)
        await self._check_layer_changed(prev_layer)

    def is_mod_pressed(self, mods):
        return bool(find(self.resolved_key_events, lambda e:
            e.hid_results is not None and
            e.hid_results.keycode is None and
            e.hid_results.mods & (KC_LSFT | KC_RSFT) > 0))

    def is_shift_pressed(self):
        return self.is_mod_pressed(KC_LSFT | KC_RSFT)

    def is_caps_locked(self):
        return (self._hid_host_report_mods & KC_CAPSLOCK) > 0

    def is_shifted(self):
        s = self.is_shift_pressed()
        if self.is_caps_locked():
            return not s
        return s

    def is_key_pressed(self, key):
        return bool(find(self.resolved_key_events, lambda i: i.key == key))

    async def press_key(self, key):
        key_event = await KeyEvent.virtual(self, key, True)
        self.resolved_key_events.append(key_event)
        await self._send_hid()

    async def release_key(self, key):
        key_event = await KeyEvent.virtual(self, key, False)
        self.resolved_key_events.append(key_event)
        await self._send_hid()

    async def tap_key(self, key):
        await self.press_key(key)
        await self.release_key(key)

    async def unlock_caps(self):
        if self.is_caps_locked():
            await self.tap_key(KC.CAPS)

    async def lock_caps(self):
        if not self.is_caps_locked():
            await self.tap_key(KC.CAPS)

    def set_lock(self, locked):
        self.hid.locked = locked
