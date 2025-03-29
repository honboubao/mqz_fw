from asyncio import sleep
from misc.time import now, time_diff, time_add

class LED_STATUS:
    STARTUP = 0
    USB_CONNECTING = 1
    USB_CONNECTED = 2
    BLE_CONNECTING = 3
    BLE_CONNECTED = 4
    LOW_BATTERY = 5


class StatusLed:

    def __init__(self):
        self.status = None
        self.color = None
        self.keyframes = None
        self.battery_level = None

    def deinit(self):
        pass

    def set_status(self, status):
        pass

    def set_led(self, rgba_color):
        pass

    def set_color(self, color):
        self.status = None
        self.keyframes = None
        self.color = color
        self.set_led(color)

    def set_animation(self, keyframes, frequency=1):
        """
        Args:
            keyframes (list of tuples): Each tuple contains a time value (between 0-1) and an RGB color tuple and an optional easing function.
            frequency (float): How fast the animation plays in Hz
        """
        self.status = None
        self.color = None
        self.keyframes = keyframes
        if keyframes[0][0] > 0:
            self.keyframes.insert(0, [0] + keyframes[-1][1:])
        if keyframes[-1][0] < 1:
            self.keyframes.append([1] + keyframes[0][1:])
        self.period_length = int(1000 / frequency)
        self.period_start = now()

    async def run(self, hid, ble_mode):
        connected_led_status = LED_STATUS.BLE_CONNECTED if ble_mode else LED_STATUS.USB_CONNECTED
        connecting_led_status = LED_STATUS.BLE_CONNECTING if ble_mode else LED_STATUS.USB_CONNECTING

        while True:
            if not hid.is_connected():
                self.set_status(connecting_led_status)
            elif self.battery_level is not None and self.battery_level < 10:
                self.set_status(LED_STATUS.LOW_BATTERY)
            else:
                self.set_status(connected_led_status)

            self.animation_tick()
            await sleep(0.03)

    def animation_tick(self):
        if self.color is not None or self.keyframes is None:
            return
        period_progression = time_diff(now(), self.period_start) / self.period_length
        if period_progression >= 1:
            period_progression = period_progression - int(period_progression)
            self.period_start = time_add(self.period_start, self.period_length)

        color = self.interpolate_color(period_progression)
        self.set_led(color)

    def interpolate_color(self, tick):

        length = len(self.keyframes)
        if length == 1:
            return self.keyframes[0][1]

        # Find keyframes that bracket the tick value
        for i in range(length - 1):
            if tick >= self.keyframes[i][0] and tick < self.keyframes[i + 1][0]:
                start_time = self.keyframes[i][0]
                start_color = self.keyframes[i][1]
                end_time = self.keyframes[i + 1][0]
                end_color = self.keyframes[i + 1][1]

                # Interpolate between start and end color based on tick position
                alpha = (tick - start_time) / (end_time - start_time)
                if len(self.keyframes[i]) > 2:
                    easing = self.keyframes[i][2]
                    alpha = easing(alpha)
                r = start_color[0] + alpha * (end_color[0] - start_color[0])
                g = start_color[1] + alpha * (end_color[1] - start_color[1])
                b = start_color[2] + alpha * (end_color[2] - start_color[2])
                a = start_color[3] + alpha * (end_color[3] - start_color[3])

                return (r, g, b, a)

        return (0, 0, 0, 0)


class SimpleStatusLed(StatusLed):

    def __init__(self, led_pin):
        super().__init__()
        import pwmio
        self.led = pwmio.PWMOut(led_pin, frequency=5000, duty_cycle=0)

    def deinit(self):
        self.led.deinit()

    def set_led(self, rgba_color):
        self.led.duty_cycle = int(65535 * rgba_color[0] * rgba_color[1] * rgba_color[2] * rgba_color[3])

    def set_status(self, status):
        if self.status == status:
            return

        if status == LED_STATUS.STARTUP:
            self.set_color((1, 1, 1, .5))
        elif status == LED_STATUS.USB_CONNECTING:
            self.set_animation([[0, (1, 1, 1, .05)], [.5, (0, 0, 0, 0)]], 2)
        elif status == LED_STATUS.USB_CONNECTED:
            self.set_color((1, 1, 1, .01))
        elif status == LED_STATUS.BLE_CONNECTING:
            self.set_animation([[0, (1, 1, 1, .05)], [.5, (0, 0, 0, 0)]])
        elif status == LED_STATUS.BLE_CONNECTED:
            self.set_animation([
                [0,   (1, 1, 1, .01)],
                [.9,  (1, 1, 1, .01)],
                [.95, (0, 0, 0, 0)]],
                .25)
        elif status == LED_STATUS.LOW_BATTERY:
            self.set_animation([
                [0,   (1, 1, 1, .05)],
                [.02, (1, 1, 1, .01)],
                [.04, (1, 1, 1, .05)],
                [.06, (1, 1, 1, .01)],
                [1,   (1, 1, 1, .01)]],
                .2)

        self.status = status

class DotStarStatusLed(StatusLed):

    def __init__(self, pin_1, pin_2):
        super().__init__()
        import adafruit_dotstar
        self.pixels = adafruit_dotstar.DotStar(pin_1, pin_2, 1)

    def deinit(self):
        self.pixels.deinit()

    def set_led(self, rgba_color):
        self.pixels[0] = rgba_color

    def set_status(self, status):
        if self.status == status:
            return

        if status == LED_STATUS.STARTUP:
            self.set_color((0, 0, 1, .5))
        elif status == LED_STATUS.USB_CONNECTED:
            self.set_color((0, 1, 0, .05))
        elif status == LED_STATUS.BLE_CONNECTING:
            self.set_animation([[0, (0, 0, 1, .1)], [.5, (0, 0, 0, 0)]])
        elif status == LED_STATUS.BLE_CONNECTED:
            self.set_color((0, 0, 1, .05))
        elif status == LED_STATUS.LOW_BATTERY:
            self.set_color((1, 0, 0, .05))

        self.status = status
