import time
import cv2
import smbus
import sun_functions
import multiplexer_functions
from eclipse_class import PiCameraStream

# Falta:
# Ver tag de la foto para transmision SSTV.


class EclipsePayload:
    """
    Class for the 4 RPI-camera payload in the Eclipse sounding balloon. 
    """
    def __init__(self, f1Pin=11, f2Pin=12, ePin=7):
        """
        Set the required pins and initialize multiplexer. 
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
            self.vs.start()
            stream = self.vs.stream
            cn = 0
            r_sun = r_sun
            camera_number = 1
            multiplexer_functions.select_camera(self.bus, self.f1Pin, self.f2Pin, self.ePin, camera_number)
            time.sleep(2.0)
            for (ii, f) in enumerate(stream):
                frame = f.array
                print 'Frame number: ', ii, ' / ', camera_number
                try:
                    crop_sun_img = sun_functions.sun_detect(frame, r_sun)
                    aux_dir = sun_img_dir + '/frame_%d_sun_%d.jpg' % (ii, cn)
                    cv2.imwrite(aux_dir, crop_sun_img)
                    self.last_pic = aux_dir
                except Exception as e:
                    cn += 1
                    print 'Exception: ', ii, ' / ', cn, ' / ', camera_number
                    camera_number = (cn%4) + 1
                    multiplexer_functions.force_camera_change(self.bus, self.f1Pin, self.f2Pin, self.ePin, camera_number)
                self.vs.rawCapture.truncate(0)
        except Exception as e:
            print 'There is an Exception: ', str(e)
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
        self.start()


if __name__ == "__main__":
    task = EclipsePayload()
    task.start()
    task.stop()
