from time import strftime
from datetime import datetime
import os

# 1.- Main code.
while True:
    tm = datetime.now().strftime('%d_%m_-_%H_%M_%S_%f')
    task = 'raspistill -n -t 1 -md 2 -ss 200000 -ISO 400 -o /home/pi/Desktop/Github/RPI_Eclipse/img_%s.jpg' %(tm)
    os.system(task)
    time.sleep(1)
