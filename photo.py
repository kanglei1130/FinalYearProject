import RPi.GPIO as GPIO
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
i = 0;
font = cv2.FONT_HERSHEY_SIMPLEX

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print 'Start'
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    input_state = GPIO.input(21)
    image = frame.array
    image = image[80:440,0:640]
    cv2.imshow("Frame", image)
    
        
    if input_state == True:
        i+=1
        print 'Stop_'+ str(i) +'.png Saved!... waiting 3 seconds'
        cv2.imwrite('STOP/Stop_'+ str(i) +'.png',image)
        
        time.sleep(3)
        
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
