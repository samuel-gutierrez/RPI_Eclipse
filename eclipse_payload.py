import os
import cv2
import time
import smbus
import sun_functions
import datetime as dt
import multiplexer_functions
from eclipse_class import PiCameraStream


class EclipsePayload:
    """
    Class for the 4 RPI-camera payload in the Eclipse sounding balloon. 
    """
    def __init__(self, f1Pin=35, f2Pin=33, ePin=15):
        """
        Set the required pins and initialize multiplexer. 
        """
        self.f1Pin = f1Pin
        self.f2Pin = f2Pin
        self.ePin = ePin
        self.bus = smbus.SMBus(1)
        multiplexer_functions.start_multiplexer(self.bus, self.f1Pin, self.f2Pin, self.ePin)
        self.vs = PiCameraStream()
        self.sun_last_pic = ''
        self.test_last_pic = ''


    def reset_defaults_parameters(self, f1Pin=35, f2Pin=33, ePin=15):
        """
        If there is an exception, this function reset the defaults parameters.
        """
        self.f1Pin = f1Pin
        self.f2Pin = f2Pin
        self.ePin = ePin
        self.bus = smbus.SMBus(1)
        multiplexer_functions.start_multiplexer(self.bus, self.f1Pin, self.f2Pin, self.ePin)
        self.vs = PiCameraStream()
        self.sun_last_pic = ''
        self.test_last_pic = ''


    def start(self):
        """
        Initialize continuous capture from camera and sun analyzing. 
        """
        try:
            while True:
                self.sun_capture()
                self.take_test_pictures()
        except Exception as e:
            print 'There is an exception: ', str(e)
            self.restart()


    def stop(self):
        """
        Stop the continuous capture from camera. 
        """
        self.vs.stop()
  
  
    def restart(self):
        """
        Restart payload. 
        """
        self.stop()
        time.sleep(1.0)
        self.reset_defaults_parameters()
        time.sleep(1.0)
        self.start()


    def sun_capture(self, r_sun=150, sun_img_dir='/home/pi/Sun_pictures'):
        self.vs.start()
        stream = self.vs.stream
        cn = 0
        camera_number = 1
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, camera_number)
        time.sleep(1.0)
        for (ii, f) in enumerate(stream):
            frame = f.array
            print 'Frame number: ', ii, ' / Camera number: ', camera_number
            # frame_pic_dir = '/home/pi/Frame_pictures/frame_%d_cam_%d.jpg' %(ii, camera_number)
            # cv2.imwrite(frame_pic_dir, frame)
            try:
                crop_sun_img = sun_functions.sun_detect(frame, r_sun)
                aux_counter = 1 + ii - cn
                dtime = dt.datetime.now()
                str_dtime = str(dtime.hour) + '_' + str(dtime.minute) + '_' + str(dtime.second)
                aux_dir = sun_img_dir + '/img_%d_frame_%d_cam_%d_' + str_dtime + '.jpg' % (aux_counter, ii, camera_number)
                cv2.imwrite(aux_dir, crop_sun_img)
                self.sun_last_pic = aux_dir
            except Exception as e:
                cn += 1
                print 'There is an exception: ', str(e)
                camera_number = (cn%4) + 1
                multiplexer_functions.force_camera_change(self.bus, self.f1Pin, self.f2Pin, self.ePin, camera_number)
            self.vs.rawCapture.truncate(0)
            if ii == 500:
                break


    def take_test_pictures(self, test_img_dir='/home/pi/Test_pictures'):
        """
        Stop the analysis of pictures of the sun, and take normal pictures with the 4 RPI cameras.
        """
        self.stop
        time.sleep(1.0)
        dtime = dt.datetime.now()
        str_dtime = str(dtime.hour) + '_' + str(dtime.minute) + '_' + str(dtime.second)
        img_task = 'raspistill -n -t 1 -o ' + test_img_dir
        multiplexer_functions.gpio_setup(self.f1Pin, self.f2Pin, self.ePin)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 1)
        img_task1 = img_task + '/img_cam_1_time_' + str_dtime + '.jpg'
        os.system(img_task1)
        time.sleep(1.0)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 2)
        img_task2 = img_task + '/img_cam_2_time_' + str_dtime + '.jpg'
        os.system(img_task2)
        time.sleep(1.0)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 3)
        img_task3 = img_task + '/img_cam_3_' + str_dtime + '.jpg'
        os.system(img_task3)
        time.sleep(1.0)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 4)
        img_task4 = img_task + '/img_cam_4_' + str_dtime + '.jpg'
        os.system(img_task4)
        time.sleep(1.0)
        self.test_last_pic = test_img_dir + '/img_cam_X_' + str_dtime + '.jpg' 
        multiplexer_functions.gpio_set_camera(self.f1Pin, self.f2Pin, self.ePin, 1)
        time.sleep(1.0)
        self.reset_defaults_parameters()


if __name__ == "__main__":
    task = EclipsePayload()
    task.start()
    task.stop()
