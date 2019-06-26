"""
A set of functions to use the camera multiplexer with the Raspberry Pi
"""
import RPi.GPIO as gp
import time


def write_register(bus, data):
    """
    Write data to address using I2C
    --------------------------
    Input : Bus, data to send
    Output: 0 is done
    """
    iic_address = (0x70)
    iic_register = (0x00)
    bus.write_byte_data(iic_address, iic_register, data)
    return 0


def gpio_setup(f1Pin, f2Pin, ePin):
    """
    Set the pins to start the use of the multiplexer
    --------------------------
    Input : Number of 3 used pins
    Output: 0 is done
    """
    gp.setwarnings(False)
    gp.setmode(gp.BOARD)
    gp.setup(f1Pin, gp.OUT)
    gp.setup(f2Pin, gp.OUT)
    gp.setup(ePin, gp.OUT)
    gp.output(f1Pin, False)
    gp.output(f2Pin, True)
    gp.output(ePin, False)
    return 0


def start_multiplexer(bus, f1Pin, f2Pin, ePin):
    """
    Set pins and write register to start the use of the multiplexer
    --------------------------
    Input : Bus, number of 3 used pins
    Output: 0 is done
    """
    try:
        write_register(bus, (0x01))
    except Exception as e:
        try:
            write_register(bus, (0x01))
        except Exception as e:
            pass
    gpio_setup(f1Pin, f2Pin, ePin)
    return 0


def gpio_set_camera(f1Pin, f2Pin, ePin, camera):
    """
    Set the pins in the GPIO based on the selected camera
    --------------------------
    Input : Number of 3 used pins, number of camera to use
    Output: 0 is done
    """
    if camera == 1:
        gp.output(f1Pin, False)
        gp.output(f2Pin, True)
        gp.output(ePin, False)
    elif camera == 2:
        gp.output(f1Pin, False)
        gp.output(f2Pin, True)
        gp.output(ePin, True)
    elif camera == 3:
        gp.output(f1Pin, True)
        gp.output(f2Pin, False)
        gp.output(ePin, False)
    elif camera == 4:
        gp.output(f1Pin, True)
        gp.output(f2Pin, False)
        gp.output(ePin, True)
    else:
        raise ValueError('==> ERROR: The multiplexer only have 4 cameras!')
    return 0


def select_camera(bus, f1Pin, f2Pin, ePin, cam_number):
    """
    Select a camera in the multiplexer
    --------------------------
    Input : Bus, 3 used pins, number of camera to use
    Output: 0 is done
    """
    if cam_number == 1:
        write_register(bus, (0x01))
        gpio_set_camera(f1Pin, f2Pin, ePin, 1)
    elif cam_number == 2:
        write_register(bus, (0x02))
        gpio_set_camera(f1Pin, f2Pin, ePin, 2)
    elif cam_number == 3:
        write_register(bus, (0x04))
        gpio_set_camera(f1Pin, f2Pin, ePin, 3)
    elif cam_number == 4:
        write_register(bus, (0x08))
        gpio_set_camera(f1Pin, f2Pin, ePin, 4)
    else:
        raise ValueError('==> ERROR: The multiplexer only have 4 cameras!')
    return 0


def force_camera_change(bus, f1Pin, f2Pin, ePin, camera_number):
    """
    Change to the next available camera using the multiplexer. If there is an I/O Exception, it tries again.
    --------------------------
    Input : Bus, 3 used pins, number of camera to change, file to write the possible generated exception
    Output: 0 is done
    """
    try:
        time.sleep(0.1)
        select_camera(bus, f1Pin, f2Pin, ePin, camera_number)
        time.sleep(0.1)
    except Exception as e:
        try:
            time.sleep(0.1)
            select_camera(bus, f1Pin, f2Pin, ePin, camera_number)
            time.sleep(0.1)
        except Exception as e:
            pass
    return 0


def force_camera_change_save_exception(bus, f1Pin, f2Pin, ePin, camera_number, error_data_file):
    """
    Change to the next available camera using the multiplexer. If there is an I/O Exception, it tries again.
    --------------------------
    Input : Bus, 3 used pins, number of camera to change, file to write the possible generated exception
    Output: 0 is done
    """
    try:
        select_camera(bus, f1Pin, f2Pin, ePin, camera_number)
        time.sleep(0.2)
    except Exception as e:
        try:
            select_camera(bus, f1Pin, f2Pin, ePin, camera_number)
            to_write = str(ii) + ' - ' + str(e) + '\n'
            error_data_file.write(to_write)
        except Exception as e:
            pass
    return 0
