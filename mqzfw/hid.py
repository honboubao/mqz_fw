from asyncio import sleep
import traceback
import time
import usb_hid
from micropython import const

from storage import getmount
from misc.time import now, time_diff

try:
    from adafruit_ble import BLERadio
    from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
    from adafruit_ble.services.standard.hid import HIDService
    from adafruit_ble.services.standard import BatteryService

    ble = BLERadio()
    ble.stop_advertising()

    BLE_APPEARANCE_HID_KEYBOARD = const(961)

    ble_hid = HIDService()
    ble_hid.protocol_mode = 0  # Boot protocol
    ble_battery = BatteryService()
    ble_advertisement = ProvideServicesAdvertisement(ble_hid)
    ble_advertisement.appearance = BLE_APPEARANCE_HID_KEYBOARD
    ble_advertisement.services.append(ble_battery)
except ImportError:
    # BLE not supported on this platform
    pass


class HIDReportTypes:
    KEYBOARD = 1
    MOUSE = 2
    CONSUMER = 3


class HIDUsage:
    KEYBOARD = 0x06
    MOUSE = 0x02
    CONSUMER = 0x01


class HIDUsagePage:
    CONSUMER = 0x0C
    KEYBOARD = MOUSE = 0x01


HID_REPORT_SIZES = {
    HIDReportTypes.KEYBOARD: 8,
    HIDReportTypes.MOUSE: 4,
    HIDReportTypes.CONSUMER: 2
}


class HIDReportData:
    def __init__(self, hid_report_type):
        self.type = hid_report_type
        self.size = HID_REPORT_SIZES[hid_report_type]
        self._prev_evt = bytearray(self.size)
        self._evt = bytearray(self.size)
        self._empty_evt = bytearray(self.size)

    def process(self, hid_results):
        pass

    def get_events(self):
        if self._evt != self._prev_evt:
            return [self._evt]
        return []

    def get_empty_event(self):
        return self._empty_evt

    def clear(self):
        for idx in range(0, self.size):
            self._evt[idx] = 0x00

    def event_sent(self):
        self._prev_evt[:] = self._evt

    def empty_event_sent(self):
        self._prev_evt[:] = self._empty_evt

class KeyboardReportData(HIDReportData):
    # 8 bytes
    #   0: mods
    #   1: padding
    #   2: keycode
    #   3: keycode
    #   4: keycode
    #   5: keycode
    #   6: keycode
    #   7: keycode
    def __init__(self):
        super().__init__(HIDReportTypes.KEYBOARD)

    def process(self, hid_results):
        self.add_keycode(hid_results.keycode)
        self.add_modifier(hid_results.mods)
        self.remove_modifier(hid_results.disable_mods)

    def add_modifier(self, modifier):
        self._evt[0] |= modifier

    def remove_modifier(self, modifier):
        self._evt[0] &= ~modifier

    def add_keycode(self, keycode):
        if keycode is not None:
            for idx in range(2, self.size):
                if self._evt[idx] == 0x00:
                    self._evt[idx] = keycode
                    break

    def get_events(self):
        if self._evt != self._prev_evt:
            events = [self._evt]
            # send mods in a separate event for events that trigger mod and key simultaneously
            # press mods first for press events
            if self._prev_evt == self._empty_evt and self._evt[0] > 0 and [kc for kc in self._evt[1:] if kc > 0]:
                mods_evt = self._empty_evt[:]
                mods_evt[0] = self._evt[0]
                events.insert(0, mods_evt)
            # keep mods pressed first for release events
            if self._evt == self._empty_evt and self._prev_evt[0] > 0 and [kc for kc in self._prev_evt[1:] if kc > 0]:
                mods_evt = self._empty_evt[:]
                mods_evt[0] = self._prev_evt[0]
                events.insert(0, mods_evt)
            return events
        return []

# class ConsumerReportData(HIDReportData):
#     def __init__(self):
#         super().__init__(HIDReportTypes.CONSUMER)

#     def process(self, hid_results):
#         self.add_keycode(hid_results.keycode)

#     def add_keycode(self, keycode):
#         # TODO support 2-byte keycodes?
#         if keycode is not None:
#             for idx in range(0, self.size):
#                 if self._evt[idx] == 0x00:
#                     self._evt[idx] = keycode
#                     break


class MouseReportData(HIDReportData):
    # 4 bytes
    #   0: buttons
    #   1: X
    #   2: Y
    #   3: wheel
    def __init__(self):
        super().__init__(HIDReportTypes.MOUSE)

    def process(self, hid_results):
        self.add_button(hid_results.keycode)

    def add_button(self, button):
        self._evt[0] |= button

    # TODO X, Y, wheel


class AbstractHID:

    def __init__(self, **kwargs):
        self.reports = {
            HIDReportTypes.KEYBOARD: KeyboardReportData(),
            # HIDReportTypes.CONSUMER: ConsumerReportData(),
            HIDReportTypes.MOUSE: MouseReportData()
        }
        self.previous_send_time = {}
        self.locked = False
        self.post_init()

    def __repr__(self):
        return '{}'.format(self.__class__.__name__)

    def post_init(self):
        pass

    def create_report(self, resolved_key_events):
        for report in self.reports.values():
            report.clear()

        for kevent in resolved_key_events:
            if kevent.hid_results is not None and kevent.hid_results.hid_type in self.reports:
                self.reports[kevent.hid_results.hid_type].process(kevent.hid_results)

    async def hid_send(self, hid_report_type, evt):
        pass

    async def hid_send_delay(self, hid_report_type):
        if hid_report_type in self.previous_send_time:
            ticks_since_prev_send = time_diff(now(), self.previous_send_time[hid_report_type])
            wait_ticks = 50 - ticks_since_prev_send
            if wait_ticks > 0:
                await sleep(wait_ticks / 1000)
        self.previous_send_time[hid_report_type] = now()

    async def send(self):
        for type, report in self.reports.items():
            if self.locked:
                await self.hid_send(type, report.get_empty_event())
                report.empty_event_sent()
            else:
                for evt in report.get_events():
                    await self.hid_send(type, evt)
                report.event_sent()

    def get_host_report(self):
        return None

    def is_connected(self):
        return False

class USBHID(AbstractHID):
    def __init__(self):
        super().__init__()
        self.ready = False

    def post_init(self):
        self.devices = {}

        for device in usb_hid.devices:
            us = device.usage
            up = device.usage_page

            # if up == HIDUsagePage.CONSUMER and us == HIDUsage.CONSUMER:
            #     self.devices[HIDReportTypes.CONSUMER] = device
            if up == HIDUsagePage.KEYBOARD and us == HIDUsage.KEYBOARD:
                self.devices[HIDReportTypes.KEYBOARD] = device
            elif up == HIDUsagePage.MOUSE and us == HIDUsage.MOUSE:
                self.devices[HIDReportTypes.MOUSE] = device

    async def send(self):
        try:
            await super().send()
            self.ready = True
        except OSError as e:
            self.ready = False

    async def hid_send(self, hid_report_type, evt):
        if hid_report_type in self.devices:
            await self.hid_send_delay(hid_report_type)
            self.devices[hid_report_type].send_report(evt)
            self.ready = True

    def get_host_report(self):
        if HIDReportTypes.KEYBOARD in self.devices:
           return self.devices[HIDReportTypes.KEYBOARD].get_last_received_report()
        return None

    def is_connected(self):
        return self.ready

class BLEHID(AbstractHID):
    def __init__(self, ble_name=str(getmount('/').label), **kwargs):
        self.ble = ble
        ble.name = ble_name
        super().__init__()

    def __repr__(self):
        return '<{}: connected={}, advertising={}, connections={}, paired={}>'.format(
            self.__class__.__name__, ble.connected, ble.advertising, ble.connections, [c.paired for c in ble.connections])

    def post_init(self):

        self.devices = {}
        self.host_report_device = None

        for device in ble_hid.devices:
            us = device.usage
            up = device.usage_page

            if hasattr(device, 'report'):
                if up == HIDUsagePage.KEYBOARD and us == HIDUsage.KEYBOARD:
                    self.host_report_device = device
            elif hasattr(device, 'send_report'):
                # if up == HIDUsagePage.CONSUMER and us == HIDUsage.CONSUMER:
                #     self.devices[HIDReportTypes.CONSUMER] = device
                if up == HIDUsagePage.KEYBOARD and us == HIDUsage.KEYBOARD:
                    self.devices[HIDReportTypes.KEYBOARD] = device
                elif up == HIDUsagePage.MOUSE and us == HIDUsage.MOUSE:
                    self.devices[HIDReportTypes.MOUSE] = device

        self.start_advertising()

    async def hid_send(self, hid_report_type, evt):
        if not ble.connected:
            return

        # the hid report would be sent to every connected host,
        # so make sure there's only one host connected
        if len(ble.connections) > 1:
            for c in ble.connections[1:]:
                c.disconnect()

        # make sure we are talking over a secured channel to the host
        if not ble.connections[0].paired:
            ble.connections[0].pair()

        if hid_report_type in self.devices:
            await self.hid_send_delay(hid_report_type)
            try:
                self.devices[hid_report_type].send_report(evt)
            except ConnectionError as e:
                traceback.print_exception(e)

    def get_host_report(self):
        if self.host_report_device:
           return self.host_report_device.report
        return None

    def clear_bonds(self):
        import _bleio

        _bleio.adapter.erase_bonding()

    def start_advertising(self):
        self.stop_advertising()

        # disconnect all hosts so the host connecting to this
        # advertisement will be the only one
        if ble.connected:
            for c in ble.connections:
                c.disconnect()

        ble.start_advertising(ble_advertisement)

    def stop_advertising(self):
        ble.stop_advertising()

    def is_connected(self):
        return ble.connected

    def send_battery_level(self, battery_level):
        if not ble.connected:
            return
        ble_battery.level = battery_level
