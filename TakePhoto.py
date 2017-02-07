from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import sys
import getch

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
s = 0;
l = 0;
r = 0;
t = 0;
#camera.color_effects = (128,128)


time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    image = image[80:440,0:640]
    
    cv2.imshow("Frame", image)
    if getch.getch() == 'l':
        print getch.getch()
        i+=1
        print 'Left_'+ str(i) +'.png Saved!... waiting 5 seconds'
        cv2.imwrite('LEFT/Left_'+ str(i) +'.png',image)
        time.sleep(5)
                   
    elif getch.getch() == 'l':
        j+=1
        print 'Right_'+ str(j) +'.png Saved!... waiting 5 seconds'
        cv2.imwrite('RIGHT/Right_'+ str(j) +'.png',image)
        time.sleep(5)
                   
    elif getch.getch() == 'l':
        k+=1
        print 'Stop_'+ str(k) +'.png Saved!... waiting 5 seconds'
        cv2.imwrite('STOP/Stop_'+ str(k) +'.png',image)
        time.sleep(5)

    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

