import sys
import memorymap
import re
from collections import namedtuple
from array import array

battery_readings_size = 10
battery_readings_pointer = 0
battery_readings = array('d')


def get_battery_percentage():
    return round(voltage_to_percentage(get_battery_voltage()))

def get_battery_voltage():
    global battery_readings
    global battery_readings_pointer
    voltage = nrf_saadc_read_vddhdiv5_voltage()
    if battery_readings_pointer >= len(battery_readings):
        battery_readings.append(voltage)
    else:
        battery_readings[battery_readings_pointer] = voltage
    battery_readings_pointer = (battery_readings_pointer + 1) % battery_readings_size
    return sum(battery_readings) / len(battery_readings)

def voltage_to_percentage(voltage):
    if voltage >= 4.2:
        return 100
    elif voltage > 4.0:
        return 85 + (voltage - 4.0) * (100 - 85) / (4.2 - 4.0)
    elif voltage > 3.9:
        return 70 + (voltage - 3.9) * (85 - 70) / (4.0 - 3.9)
    elif voltage > 3.8:
        return 50 + (voltage - 3.8) * (70 - 50) / (3.9 - 3.8)
    elif voltage > 3.7:
        return 30 + (voltage - 3.7) * (50 - 30) / (3.8 - 3.7)
    elif voltage > 3.5:
        return 15 + (voltage - 3.5) * (30 - 15) / (3.7 - 3.5)
    elif voltage > 3.2:
        return 5 + (voltage - 3.2) * (15 - 5) / (3.5 - 3.2)
    elif voltage > 3.0:
        return (voltage - 3.0) * (5 - 0) / (3.2 - 3.0)
    else:
        return 0

def set_address_uint32(addr, value):
    data = value.to_bytes(4, sys.byteorder)
    register = memorymap.AddressRange(start=addr, length=4)
    register[:] = data

def get_address_uint32(addr):
    register = memorymap.AddressRange(start=addr, length=4)
    data = int.from_bytes(register[:], sys.byteorder)
    return data

#######################################################################################################################
# SYSTEMOFF
#
# nRF52 Series > nRF52840 > nRF52840 Product Specification > Power and clock management > POWER — Power supply > Registers > SYSTEMOFF
# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fps_nrf52840%2Fpower.html&cp=5_0_0_4_2_2&anchor=register.SYSTEMOFF
#
# nRF52 Series > nRF52840 > nRF52840 Product Specification > Peripherals > GPIO — General purpose input/output
# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fps_nrf52840%2Fgpio.html&cp=5_0_0_5_8

system_off_addr = 0x40000500

GPIO_BASE = 0x50000000
GPIO_PORT_0_OFFSET = 0x00000000
GPIO_PORT_1_OFFSET = 0x00000300
GPIO_PIN_CNF_OFFSET = 0x700
GPIO_PIN_CNF_SIZE = 4
#          input   buffer     pull up    sense low
# 0x0003000C = 0 | (0 << 1) | (3 << 2) | (3 << 16)
GPIO_PIN_CNF = 0x0003000C

PIN_NAME_REGEX = re.compile('board\\.P[01]_[0-3][0-9]')

def get_pin_cnf_address(pin):
    pin_string = str(pin)
    if not PIN_NAME_REGEX.match(pin_string):
        raise Exception('Cannot resolve address for Pin ' + pin_string + '. Pin must be a board.PX_XX pin.')

    port_no, pin_no = [int(i) for i in pin_string[7:].split('_')]

    if pin_no < 0 or pin_no > 31:
        raise Exception('Cannot resolve address for Pin ' + pin_string + '. Unknown pin number.')

    return GPIO_BASE + (GPIO_PORT_0_OFFSET if port_no == 0 else GPIO_PORT_1_OFFSET) + GPIO_PIN_CNF_OFFSET + pin_no * GPIO_PIN_CNF_SIZE


def deep_sleep(alarm_pin):
    # see also:
    # nRF: deep sleep increases power usage https://github.com/adafruit/circuitpython/issues/5318
    pin_cnf_addr = get_pin_cnf_address(alarm_pin)
    set_address_uint32(pin_cnf_addr, GPIO_PIN_CNF)
    set_address_uint32(system_off_addr, 1)


#######################################################################################################################
# SAADC
#
# nRF52 Series > nRF52840 > nRF52840 Product Specification > Peripherals >
#   SAADC — Successive approximation analog-to-digital converter
# https://infocenter.nordicsemi.com/index.jsp?topic=%2Fps_nrf52840%2Fsaadc.html&cp=5_0_0_5_22

# SAADC registers
NRF_SAADC_BASE = 0x40007000
NRF_SAADC_TASKS_START_OFFSET = 0x00000000
NRF_SAADC_TASKS_SAMPLE_OFFSET = 0x00000004
NRF_SAADC_TASKS_STOP_OFFSET = 0x00000008
NRF_SAADC_TASKS_CALIBRATEOFFSET_OFFSET = 0x0000000C
NRF_SAADC_EVENTS_STARTED_OFFSET = 0x00000100
NRF_SAADC_EVENTS_END_OFFSET = 0x00000104
NRF_SAADC_EVENTS_DONE_OFFSET = 0x00000108
NRF_SAADC_EVENTS_RESULTDONE_OFFSET = 0x0000010C
NRF_SAADC_EVENTS_CALIBRATEDONE_OFFSET = 0x00000110
NRF_SAADC_EVENTS_STOPPED_OFFSET = 0x00000114
NRF_SAADC_EVENTS_CH_OFFSET = 0x00000118
NRF_SAADC_INTEN_OFFSET = 0x00000300
NRF_SAADC_INTENSET_OFFSET = 0x00000304
NRF_SAADC_INTENCLR_OFFSET = 0x00000308
NRF_SAADC_STATUS_OFFSET = 0x00000400
NRF_SAADC_ENABLE_OFFSET = 0x00000500
NRF_SAADC_CH_OFFSET = 0x00000510
NRF_SAADC_RESOLUTION_OFFSET = 0x000005F0
NRF_SAADC_OVERSAMPLE_OFFSET = 0x000005F4
NRF_SAADC_SAMPLERATE_OFFSET = 0x000005F8
NRF_SAADC_RESULT_OFFSET = 0x0000062C

NRF_SAADC_CH_NUM = 8
NRF_SAADC_CH_SIZE = 16
NRF_SAADC_CH_PSELP_OFFSET  = 0x00000000
NRF_SAADC_CH_PSELN_OFFSET  = 0x00000004
NRF_SAADC_CH_CONFIG_OFFSET = 0x00000008
NRF_SAADC_CH_LIMIT_OFFSET  = 0x0000000C

NRF_SAADC_RESULT_PTR_OFFSET    = 0x00000000
NRF_SAADC_RESULT_MAXCNT_OFFSET = 0x00000004
NRF_SAADC_RESULT_AMOUNT_OFFSET = 0x00000008

# register values
NRF_SAADC_RESOLUTION_8BIT  = 0
NRF_SAADC_RESOLUTION_10BIT = 1
NRF_SAADC_RESOLUTION_12BIT = 2
NRF_SAADC_RESOLUTION_14BIT = 3

NRF_SAADC_OVERSAMPLE_DISABLED = 0
NRF_SAADC_OVERSAMPLE_2X       = 1
NRF_SAADC_OVERSAMPLE_4X       = 2
NRF_SAADC_OVERSAMPLE_8X       = 3
NRF_SAADC_OVERSAMPLE_16X      = 4
NRF_SAADC_OVERSAMPLE_32X      = 5
NRF_SAADC_OVERSAMPLE_64X      = 6
NRF_SAADC_OVERSAMPLE_128X     = 7
NRF_SAADC_OVERSAMPLE_256X     = 8

NRF_SAADC_ENABLE_DISABLED = 0
NRF_SAADC_ENABLE_ENABLED = 1

NRF_SAADC_INPUT_DISABLED = 0
NRF_SAADC_INPUT_AIN0     = 1
NRF_SAADC_INPUT_AIN1     = 2
NRF_SAADC_INPUT_AIN2     = 3
NRF_SAADC_INPUT_AIN3     = 4
NRF_SAADC_INPUT_AIN4     = 5
NRF_SAADC_INPUT_AIN5     = 6
NRF_SAADC_INPUT_AIN6     = 7
NRF_SAADC_INPUT_AIN7     = 8
NRF_SAADC_INPUT_VDD      = 9
NRF_SAADC_INPUT_VDDHDIV5 = 0x0D

NRF_SAADC_CH_CONFIG_BURST_Pos = 24
NRF_SAADC_CH_CONFIG_BURST_Msk = 0x1 << NRF_SAADC_CH_CONFIG_BURST_Pos
NRF_SAADC_CH_CONFIG_BURST_Disabled = 0
NRF_SAADC_CH_CONFIG_BURST_Enabled = 1

NRF_SAADC_CH_CONFIG_MODE_Pos = 20
NRF_SAADC_CH_CONFIG_MODE_Msk = 0x1 << NRF_SAADC_CH_CONFIG_MODE_Pos
NRF_SAADC_CH_CONFIG_MODE_SE = 0
NRF_SAADC_CH_CONFIG_MODE_Diff = 1

NRF_SAADC_CH_CONFIG_TACQ_Pos = 16
NRF_SAADC_CH_CONFIG_TACQ_Msk = 0x7 << NRF_SAADC_CH_CONFIG_TACQ_Pos
NRF_SAADC_CH_CONFIG_TACQ_3us = 0
NRF_SAADC_CH_CONFIG_TACQ_5us = 1
NRF_SAADC_CH_CONFIG_TACQ_10us = 2
NRF_SAADC_CH_CONFIG_TACQ_15us = 3
NRF_SAADC_CH_CONFIG_TACQ_20us = 4
NRF_SAADC_CH_CONFIG_TACQ_40us = 5

NRF_SAADC_CH_CONFIG_REFSEL_Pos = 12
NRF_SAADC_CH_CONFIG_REFSEL_Msk = 0x1 << NRF_SAADC_CH_CONFIG_REFSEL_Pos
NRF_SAADC_CH_CONFIG_REFSEL_Internal = 0
NRF_SAADC_CH_CONFIG_REFSEL_VDD1_4 = 1

NRF_SAADC_CH_CONFIG_GAIN_Pos = 8
NRF_SAADC_CH_CONFIG_GAIN_Msk = 0x7 << NRF_SAADC_CH_CONFIG_GAIN_Pos
NRF_SAADC_CH_CONFIG_GAIN_Gain1_6 = 0
NRF_SAADC_CH_CONFIG_GAIN_Gain1_5 = 1
NRF_SAADC_CH_CONFIG_GAIN_Gain1_4 = 2
NRF_SAADC_CH_CONFIG_GAIN_Gain1_3 = 3
NRF_SAADC_CH_CONFIG_GAIN_Gain1_2 = 4
NRF_SAADC_CH_CONFIG_GAIN_Gain1 = 5
NRF_SAADC_CH_CONFIG_GAIN_Gain2 = 6
NRF_SAADC_CH_CONFIG_GAIN_Gain4 = 7

NRF_SAADC_CH_CONFIG_RESN_Pos = 4
NRF_SAADC_CH_CONFIG_RESN_Msk = 0x3 << NRF_SAADC_CH_CONFIG_RESN_Pos
NRF_SAADC_CH_CONFIG_RESN_Bypass = 0
NRF_SAADC_CH_CONFIG_RESN_Pulldown = 1
NRF_SAADC_CH_CONFIG_RESN_Pullup = 2
NRF_SAADC_CH_CONFIG_RESN_VDD1_2 = 3

NRF_SAADC_CH_CONFIG_RESP_Pos = 0
NRF_SAADC_CH_CONFIG_RESP_Msk = 0x3 << NRF_SAADC_CH_CONFIG_RESP_Pos
NRF_SAADC_CH_CONFIG_RESP_Bypass = 0
NRF_SAADC_CH_CONFIG_RESP_Pulldown = 1
NRF_SAADC_CH_CONFIG_RESP_Pullup = 2
NRF_SAADC_CH_CONFIG_RESP_VDD1_2 = 3

# bytearray is represented in C as
# typedef struct _mp_obj_array_t {
#     mp_obj_base_t base;
#     size_t typecode : 8;
#     size_t free : MP_OBJ_ARRAY_FREE_SIZE_BITS;
#     size_t len;
#     void *items;
# } mp_obj_array_t;
# the items pointer holds the address of the data with an offset in memory of 12 bytes
BYTE_ARRAY_DATA_OFFSET = 0x0C
NRF_SAADC_READ_BUFFER = bytearray(4)
NRF_SAADC_READ_BUFFER_BASE = id(NRF_SAADC_READ_BUFFER)
NRF_SAADC_READ_BUFFER_DATA = NRF_SAADC_READ_BUFFER_BASE + BYTE_ARRAY_DATA_OFFSET

ChannelConfig = namedtuple("ChannelConfig", ['resistor_p', 'resistor_n', 'gain', 'reference', 'acq_time', 'mode', 'burst'])

def nrf_saadc_channel_addr(channel):
    return NRF_SAADC_BASE + NRF_SAADC_CH_OFFSET + channel * NRF_SAADC_CH_SIZE

def nrf_saadc_resolution_set(resolution):
    set_address_uint32(NRF_SAADC_BASE + NRF_SAADC_RESOLUTION_OFFSET, resolution)

def nrf_saadc_oversample_set(oversample):
    set_address_uint32(NRF_SAADC_BASE + NRF_SAADC_OVERSAMPLE_OFFSET, oversample)

def nrf_saadc_enable():
    set_address_uint32(NRF_SAADC_BASE + NRF_SAADC_ENABLE_OFFSET, NRF_SAADC_ENABLE_ENABLED)

def nrf_saadc_disable():
    set_address_uint32(NRF_SAADC_BASE + NRF_SAADC_ENABLE_OFFSET, NRF_SAADC_ENABLE_DISABLED)

def nrf_saadc_channel_input_set(channel, pselp, pseln):
    channel_addr = nrf_saadc_channel_addr(channel)
    set_address_uint32(channel_addr + NRF_SAADC_CH_PSELP_OFFSET, pselp)
    set_address_uint32(channel_addr + NRF_SAADC_CH_PSELN_OFFSET, pseln)

def nrf_saadc_channel_init(channel, config):
    channel_addr = nrf_saadc_channel_addr(channel)
    config_value = \
            ((config.resistor_p   << NRF_SAADC_CH_CONFIG_RESP_Pos)   & NRF_SAADC_CH_CONFIG_RESP_Msk) \
            | ((config.resistor_n << NRF_SAADC_CH_CONFIG_RESN_Pos)   & NRF_SAADC_CH_CONFIG_RESN_Msk) \
            | ((config.gain       << NRF_SAADC_CH_CONFIG_GAIN_Pos)   & NRF_SAADC_CH_CONFIG_GAIN_Msk) \
            | ((config.reference  << NRF_SAADC_CH_CONFIG_REFSEL_Pos) & NRF_SAADC_CH_CONFIG_REFSEL_Msk) \
            | ((config.acq_time   << NRF_SAADC_CH_CONFIG_TACQ_Pos)   & NRF_SAADC_CH_CONFIG_TACQ_Msk) \
            | ((config.mode       << NRF_SAADC_CH_CONFIG_MODE_Pos)   & NRF_SAADC_CH_CONFIG_MODE_Msk) \
            | ((config.burst      << NRF_SAADC_CH_CONFIG_BURST_Pos)  & NRF_SAADC_CH_CONFIG_BURST_Msk)
    set_address_uint32(channel_addr + NRF_SAADC_CH_CONFIG_OFFSET, config_value)

def nrf_saadc_buffer_init(buffer_addr, size):
    set_address_uint32(NRF_SAADC_BASE + NRF_SAADC_RESULT_OFFSET + NRF_SAADC_RESULT_PTR_OFFSET, buffer_addr)
    set_address_uint32(NRF_SAADC_BASE + NRF_SAADC_RESULT_OFFSET + NRF_SAADC_RESULT_MAXCNT_OFFSET, size)

def nrf_saadc_task_trigger(task_register_offset):
    set_address_uint32(NRF_SAADC_BASE + task_register_offset, 1)

def nrf_saadc_event_check(event_register_offset):
    return get_address_uint32(NRF_SAADC_BASE + event_register_offset) > 0

def nrf_saadc_event_clear(event_register_offset):
    set_address_uint32(NRF_SAADC_BASE + event_register_offset, 0)
    nrf_saadc_event_check(event_register_offset)

def nrf_saadc_read(channel_pselp, channel_pseln, config):
    channel = 0
    set_address_uint32(NRF_SAADC_READ_BUFFER_DATA, 0)

    nrf_saadc_resolution_set(NRF_SAADC_RESOLUTION_14BIT)
    nrf_saadc_oversample_set(NRF_SAADC_OVERSAMPLE_DISABLED)
    nrf_saadc_enable()

    for i in range(NRF_SAADC_CH_NUM):
        nrf_saadc_channel_input_set(i, NRF_SAADC_INPUT_DISABLED, NRF_SAADC_INPUT_DISABLED);

    nrf_saadc_channel_init(channel, config)
    nrf_saadc_channel_input_set(channel, channel_pselp, channel_pseln)
    nrf_saadc_buffer_init(NRF_SAADC_READ_BUFFER_DATA, 1)

    nrf_saadc_task_trigger(NRF_SAADC_TASKS_START_OFFSET)
    while not nrf_saadc_event_check(NRF_SAADC_EVENTS_STARTED_OFFSET):
        pass
    nrf_saadc_event_clear(NRF_SAADC_EVENTS_STARTED_OFFSET)

    nrf_saadc_task_trigger(NRF_SAADC_TASKS_SAMPLE_OFFSET)
    while not nrf_saadc_event_check(NRF_SAADC_EVENTS_END_OFFSET):
        pass
    nrf_saadc_event_clear(NRF_SAADC_EVENTS_END_OFFSET)

    nrf_saadc_task_trigger(NRF_SAADC_TASKS_STOP_OFFSET)
    while not nrf_saadc_event_check(NRF_SAADC_EVENTS_STOPPED_OFFSET):
        pass
    nrf_saadc_event_clear(NRF_SAADC_EVENTS_STOPPED_OFFSET)

    nrf_saadc_disable()

    nrf_saadc_channel_input_set(channel, NRF_SAADC_INPUT_DISABLED, NRF_SAADC_INPUT_DISABLED)

    value = get_address_uint32(NRF_SAADC_READ_BUFFER_DATA)

    if value < 0:
        value = 0

    return value

def nrf_saadc_read_vddhdiv5_voltage():
    config = ChannelConfig(
        NRF_SAADC_CH_CONFIG_RESP_Bypass,
        NRF_SAADC_CH_CONFIG_RESN_Bypass,
        NRF_SAADC_CH_CONFIG_GAIN_Gain1_6,
        NRF_SAADC_CH_CONFIG_REFSEL_Internal,
        NRF_SAADC_CH_CONFIG_TACQ_10us,
        NRF_SAADC_CH_CONFIG_MODE_SE,
        NRF_SAADC_CH_CONFIG_BURST_Disabled)
    value = nrf_saadc_read(NRF_SAADC_INPUT_VDDHDIV5, NRF_SAADC_INPUT_VDDHDIV5, config)

    # RESULT = (V(P) – V(N)) * (GAIN/REFERENCE) * 2^(RESOLUTION - m)
    #
    # RESULT = VDDHDIV5_ADC_VALUE
    # V(P) = VDDHDIV5_Voltage
    # V(N) = 0 in single-ended mode
    # GAIN = 1/6
    # REFERENCE = REFERENCE INTERNAL = 0.6 V
    # RESOLUTION = 14 bit
    # m = 0 in single-ended mode
    #
    # VDDHDIV5_ADC_VALUE = (VDDHDIV5_Voltage - 0) * ((1/6)/0.6) * 2^(14 - 0)
    # VDDHDIV5_ADC_VALUE = VDDHDIV5_Voltage  * 16384 / 6 / 0.6
    # VDDHDIV5_Voltage = VDDHDIV5_ADC_VALUE * 6 * 0.6 / 16384
    # VDDH_Voltage = VDDHDIV5_ADC_VALUE * 5 * 6 * 0.6 / 16384
    # VDDH_Voltage = VDDHDIV5_ADC_VALUE * 18 / 16384
    return value * 18 / 16383.0