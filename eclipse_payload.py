import os
import cv2
import time
import smbus
import sun_functions
import multiplexer_functions
from eclipse_class import PiCameraStream


class EclipsePayload:
    """
    Class for the 4 RPI-camera payload in the Eclipse sounding balloon. 
    """
    def __init__(self, f1Pin=33, f2Pin=31, ePin=15):
        """
        Set the required pins and initialize multiplexer. 
        """
        self.f1Pin = f1Pin
        self.f2Pin = f2Pin
        self.ePin = ePin
        self.bus = smbus.SMBus(1)
        multiplexer_functions.start_multiplexer(self.bus, self.f1Pin, self.f2Pin, self.ePin)
        self.vs = PiCameraStream(bright=50)
        self.last_pic = ''


    def reset_defaults_parameters(self, f1Pin=33, f2Pin=31, ePin=15):
        """
        If there is an exception, this function reset the defaults parameters.
        """
        self.f1Pin = f1Pin
        self.f2Pin = f2Pin
        self.ePin = ePin
        self.bus = smbus.SMBus(1)
        multiplexer_functions.start_multiplexer(self.bus, self.f1Pin, self.f2Pin, self.ePin)
        self.vs = PiCameraStream()
        self.last_pic = ''
      

    def start(self, r_sun=150, sun_img_dir='/home/pi/Sun_pictures'):
        """
        Initialize continuous capture from camera and sun analyzing. 
        """
        try:
          self.sun_capture()
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
        print '- OK - '
        stream = self.vs.stream
        cn = 0
        r_sun = r_sun
        camera_number = 1
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, camera_number)
        time.sleep(1.0)
        for (ii, f) in enumerate(stream):
            frame = f.array
            print 'Frame number: ', ii, ' / Camera number: ', camera_number
            frame_pic_dir = '/home/pi/Frame_pictures/frame_%d_cam_%d.jpg' %(ii, camera_number)
            cv2.imwrite(frame_pic_dir, frame)
            try:
                crop_sun_img = sun_functions.sun_detect(frame, r_sun)
                aux_counter = 1 + ii - cn
                aux_dir = sun_img_dir + '/img_%d_frame_%d_cam_%d.jpg' % (aux_counter, ii, camera_number)
                cv2.imwrite(aux_dir, crop_sun_img)
                self.last_pic = aux_dir
            except Exception as e:
                cn += 1
                print 'There is an exception: ', str(e)
                camera_number = (cn%4) + 1
                multiplexer_functions.force_camera_change(self.bus, self.f1Pin, self.f2Pin, self.ePin, camera_number)
            self.vs.rawCapture.truncate(0)


    def take_test_pictures(self, test_img_dir='/home/pi/test_pictures'):
        """
        Stop the analysis of pictures of the sun, and take normal pictures with the 4 RPI cameras.
        """
        self.stop
        time.sleep(1.0)
        img_task = 'raspistill -n -t 1 -o ' + test_img_dir
        multiplexer_functions.gpio_setup(self.f1Pin, self.f2Pin, self.ePin)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 1)
        img_task1 = img_task + '/img_cam_1.jpg'
        os.system(img_task1)
        time.sleep(1.0)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 2)
        img_task2 = img_task + '/img_cam_2.jpg'
        os.system(img_task2)
        time.sleep(1.0)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 3)
        img_task3 = img_task + '/img_cam_3.jpg'
        os.system(img_task3)
        time.sleep(1.0)
        multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, 4)
        img_task4 = img_task + '/img_cam_4.jpg'
        os.system(img_task4)
        time.sleep(1.0)
        multiplexer_functions.gpio_set_camera(self.f1Pin, self.f2Pin, self.ePin, 1)
        time.sleep(1.0)
        self.reset_defaults_parameters()


if __name__ == "__main__":
    task = EclipsePayload()
    task.start()
    task.stop()
    
