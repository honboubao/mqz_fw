from asyncio import sleep
from storage import getmount
from micropython import const

class BLEServices:
    def __init__(self, ble_name=str(getmount('/').label), **kwargs):
        # load only if requested. BLE is not available on all boards
        from adafruit_ble import BLERadio
        from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
        from adafruit_ble.services.standard.hid import HIDService
        from adafruit_ble.services.standard import BatteryService

        self.radio = BLERadio()
        self.radio.stop_advertising()
        self.radio.name = ble_name

        BLE_APPEARANCE_HID_KEYBOARD = const(961)

        self.hid = HIDService()
        self.hid.protocol_mode = 0  # Boot protocol
        self.battery = BatteryService()
        self.advertisement = ProvideServicesAdvertisement(self.hid)
        self.advertisement.appearance = BLE_APPEARANCE_HID_KEYBOARD
        self.advertisement.services.append(self.battery)

    def __repr__(self):
        return '<{}: connected={}, advertising={}, connections={}, paired={}>'.format(
            self.__class__.__name__, self.radio.connected, self.radio.advertising, self.radio.connections, [c.paired for c in self.radio.connections])

    def clear_bonds(self):
        import _bleio
        _bleio.adapter.erase_bonding()

    def start_advertising(self):
        self.stop_advertising()

        # disconnect all hosts so the host connecting to this
        # advertisement will be the only one
        if self.radio.connected:
            for c in self.radio.connections:
                c.disconnect()

        self.radio.start_advertising(self.advertisement)

    def stop_advertising(self):
        self.radio.stop_advertising()

    async def monitor_connection(self):
        while True:
            await self.ensure_single_host_paired()
            await sleep(0.1)

    async def ensure_single_host_paired(self):
        # the hid report would be sent to every connected host,
        # so make sure there's only one host connected
        if len(self.radio.connections) > 1:
            self.start_advertising()

        await self.ensure_connected()

        # make sure we are talking over a secured channel to the host
        if not self.radio.connections[0].paired:
            self.radio.connections[0].pair()

    async def ensure_connected(self):
        if not self.radio.connected:
            self.start_advertising()
        while not self.radio.connected:
            await sleep(0.05)

    def send_battery_level(self, battery_level):
        if not self.radio.connected:
            return
        self.battery.level = battery_level