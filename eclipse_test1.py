# 1.- Imports.
import time
import cv2
import os
import smbus
import sun_functions
import multiplexer_functions
from eclipse_class import PiCameraStream

# 2.- Set GPIO pins and initialize multiplexer and camera.
f1Pin = 11
f2Pin = 12
ePin = 7
bus = smbus.SMBus(1)
multiplexer_functions.start_multiplexer(bus, f1Pin, f2Pin, ePin)

# 3.- Define directories to use.
base_dir = '/home/pi/Desktop/Github/RPI_Eclipse/Scripts/'
file_dir = base_dir + 'data.txt'
is_file = os.path.isfile(file_dir)

# 4.- Continuosly analyze pictures.
if is_file == False:
    vs = PiCameraStream()
    stream = vs.stream
    total_frames = 50
    cn = 0
    r_sun = 150
    file = open(file_dir, 'w')
    tm1 = time.time()
    camera_number = 1
    multiplexer_functions.select_camera(bus, f1Pin, f2Pin, ePin, camera_number)
    time.sleep(2.0)

    for (ii, f) in enumerate(stream):
        tm11 = time.time()
        frame = f.array
        cv2.imwrite(base_dir + 'Pictures/frame_%d_cam_%d.jpg' % (ii, camera_number), frame)
        print ' --> Frame / camera number:  ', ii, ' / ', camera_number
        # Detect sun.
        try:
            crop_sun_img = sun_functions.sun_detect(frame, r_sun)
            cv2.imwrite(base_dir + 'Pictures/frame_sun_%d_cam_%d.jpg' % (ii, camera_number), crop_sun_img)
        except Exception as e:
            print e
            to_write = str(ii) + ' - ' + str(e) + '\n' 
            file.write(to_write)
            # Change camera.
            cn += 1
            camera_number = (cn%4) + 1
            multiplexer_functions.force_camera_change(bus, f1Pin, f2Pin, ePin, camera_number, file)
        vs.rawCapture.truncate(0)
        tm22 = time.time()
        print 'Time step:', tm22 - tm11
        if ii == total_frames:
            break
    file.close()
    tm2 = time.time()
    vs.stop()
    print '==> Total time:', tm2 - tm1
