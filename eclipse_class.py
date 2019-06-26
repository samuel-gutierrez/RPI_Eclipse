
from picamera.array import PiRGBArray
from picamera import PiCamera


class PiCameraStream:
    """
    A class to streaming frames with the PiCamera object
    """
    def __init__(self, resolution=(1648, 928), framerate=40, ss=1, ISO=100, bright=40):
        """
        Initialize the camera object with our optimal parameters
        """
	self.camera = PiCamera()
	self.camera.resolution = resolution
	self.camera.framerate = framerate
	self.camera.shutter_speed = ss
	self.camera.iso = ISO
	self.camera.awb_mode = 'sunlight'
	self.camera.brightness = bright
	
	
    def start(self):
        """
        Start image stream 
        """
	self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
	self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)


    def stop(self):
        """
        Close the camera in a properly way
        """
	self.stream.close()
        self.rawCapture.close()
        self.camera.close()
