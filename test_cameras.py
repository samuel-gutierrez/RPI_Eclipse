import os
import smbus
import multiplexer_functions

# Define GPIO pins
f1Pin, f2Pin, ePin =(33, 31, 15)

# Set multiplexer
bus = smbus.SMBus(1)
multiplexer_functions.gpio_setup(f1Pin, f2Pin, ePin)

task = 'raspistill -n -t 1 -o '
c = ''

# Test cameras
while c != 'q':
    c = raw_input("Enter camera number (q for quit):")
    if c == '1':
        multiplexer_functions.select_camera(bus, f1Pin, f2Pin, ePin, 1)
        task1 = task + '/home/pi/cam1.jpg'
        os.system(task1)
    elif c == '2':
        multiplexer_functions.select_camera(bus, f1Pin, f2Pin, ePin, 2)
        task2 = task + '/home/pi/cam2.jpg'
        os.system(task2)
    elif c == '3':
        multiplexer_functions.select_camera(bus, f1Pin, f2Pin, ePin, 3)
        task3 = task + '/home/pi/cam3.jpg'
        os.system(task3)
    elif c == '4':
        multiplexer_functions.select_camera(bus, f1Pin, f2Pin, ePin, 4)
        task4 = task + '/home/pi/cam4.jpg'
        os.system(task4)
    else:
        if c != 'q':
            print('==> ERROR: Press another key!')
        continue

multiplexer_functions.gpio_set_camera(f1Pin, f2Pin, ePin, 1)
