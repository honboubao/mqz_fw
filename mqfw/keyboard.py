from mqfw.hid import BLEHID, USBHID
from mqfw.keys import KC_CAPSLOCK, KC_LSFT, KC_RSFT
from mqfw.matrix import MatrixScanner

class Keyboard:
    debug_enabled = False

    # config
    keymap = []
    holdtaps = []
    row_pins = None
    col_pins = None
    diode_orientation = None
    hid_device = USBHID
    ble_name='CircuitPython Keyboard BLE'
    tapping_term = 300

    # state
    unresolved_key_events = []
    resolved_key_events = []
    
    _mods_active = set()
    _active_layers = [0]

    _hid = None
    _hid_host_report_mods = 0x00
    
    def go(self):
        self._init()
        while True:
            self._main_loop()

    def _log(self, message):
        if self.debug_enabled:
            print(message)

    def _init(self):
        self._hid = self.hid_device()
        # TODO what about BLE?

        self._matrix = MatrixScanner(
            cols=self.col_pins,
            rows=self.row_pins,
            diode_orientation=self.diode_orientation
        )

    def _main_loop(self):
        hid_host_report = self._hid.get_host_report()
        if hid_host_report and hid_host_report[0] != self._hid_host_report_mods:
            self._hid_host_report_mods = hid_host_report[0]

        matrix_update = self._matrix.scan_for_changes()
        if matrix_update:
            self._log('MatrixChange(ic={} pressed={})'.format(matrix_update.int_coord, matrix_update.pressed))
            self.unresolved_key_events.append(matrix_update)

        if self.unresolved_key_events:
            e = self.unresolved_key_events[0]
            e.prepare(self)
            if e.resolve():
                self.resolved_key_events.append(e)
                self.unresolved_key_events.remove(e)
            self.resolved_key_events = [e for e in self.resolved_key_events if not e.to_be_removed]

        self._send_hid()

    def _send_hid(self): 
        self._hid.create_report(self.resolved_key_events)
        self._hid.send()


    def get_keymap_key(self, int_coord):
        layer = self._active_layers[0]
        try:
            layer_key = self.keymap[layer][int_coord]
        except IndexError:
            layer_key = None
            self._log(f'KeymapIndexError(int_coord={int_coord}, layer={layer})')
        self._log('KeyResolution(key={}, layer={})'.format(layer_key, layer))

        return layer_key

    def set_layer(self, layer):
        self._active_layers.clear()
        self._active_layers.append(layer)

    def activate_layer(self, layer):
        self._active_layers.insert(0, layer)

    def deactivate_layer(self, layer):
        if layer in self._active_layers:
            self._active_layers.remove(layer)

    def is_shift_pressed(self):
        for kevent in self.resolved_key_events:
            if kevent.hid_results is None or kevent.hid_results.keycode is not None:
                continue
            
            if kevent.hid_results.mods & (KC_LSFT | KC_RSFT):
                return True
        return False

    def is_caps_locked(self):
        return (self._hid_host_report_mods & KC_CAPSLOCK) > 0

    def is_shifted(self):
        s = self.is_shift_pressed()
        if self.is_caps_locked():
            return not s
        return s