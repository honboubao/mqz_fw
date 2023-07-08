import digitalio

def switch_pressed(outputPin, inputPin):
    output = digitalio.DigitalInOut(outputPin)
    output.switch_to_output()
    input = digitalio.DigitalInOut(inputPin)
    input.switch_to_input(pull=digitalio.Pull.DOWN)

    output.value = True
    pressed = input.value
    output.value = False

    output.deinit()
    input.deinit()

    return pressed
