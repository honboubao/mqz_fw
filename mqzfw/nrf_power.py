import sys
import memorymap

# nRF52 Series > nRF52840 > nRF52840 Product Specification > Power and clock management > POWER — Power supply > Registers > SYSTEMOFF
# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fps_nrf52840%2Fpower.html&cp=5_0_0_4_2_2&anchor=register.SYSTEMOFF
system_off_addr = 0x40000500

# nRF52 Series > nRF52840 > nRF52840 Product Specification > Peripherals > GPIO — General purpose input/output
# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fps_nrf52840%2Fgpio.html&cp=5_0_0_5_8
gpio_base_addr_port0 = 0x50000000
gpio_base_addr_port1 = 0x50000300
gpio_pin_cnf_addr_offset = 0x700
pin_alarm_cnf = 0 # input buffer
pin_alarm_cnf |= 3 << 2 # pull up
pin_alarm_cnf |= 3 << 16 # sense low


def set_register_uint32(addr, value):
    data = value.to_bytes(4, sys.byteorder)
    register = memorymap.AddressRange(start=addr, length=4)
    register[:] = data


def get_pin_cnf_address(pin):
    pin_string = str(pin)
    if not pin_string.startswith('board.P'):
        raise Exception('Cannot resolve address for Pin ' + pin_string + '. Pin must be a board.P* pin.')

    pin_name = pin_string[7:]
    if pin_name.startswith('0_'):
        gpio_base_addr = gpio_base_addr_port0
    elif pin_name.startswith('1_'):
        gpio_base_addr = gpio_base_addr_port1
    else:
        raise Exception('Cannot resolve address for Pin ' + pin_string + '. Unknown pin port.')

    try:
        pin_no = int(pin_name[2:])
    except ValueError:
        raise Exception('Cannot resolve address for Pin ' + pin_string + '. Unknown non-numeric pin.')
    if pin_no < 0 or pin_no > 31:
        raise Exception('Cannot resolve address for Pin ' + pin_string + '. Unknown pin number.')

    return gpio_base_addr + gpio_pin_cnf_addr_offset + pin_no * 4


def deep_sleep(alarm_pin):
    # see also:
    # nRF: deep sleep increases power usage https://github.com/adafruit/circuitpython/issues/5318
    pin_cnf_addr = get_pin_cnf_address(alarm_pin)
    set_register_uint32(pin_cnf_addr, pin_alarm_cnf)
    set_register_uint32(system_off_addr, 1)
