from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import sys

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    
    image = frame.array
    roi = image[450:470,0:640]
    gray = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,100,200,apertureSize = 3)
    
    
    lines = cv2.HoughLinesP(edges,1,np.pi/360,5,15,2)
    cv2.rectangle(image,(0,450),(640,470),(0,0,255),2)
    cv2.line(image,(0,460),(640,460),(255,0,0),1)
    cv2.line(image,(320,440),(320,480),(255,0,0),1)
    cv2.putText(image,"Test",(290,440), font, 1,(0,255,0))
    try:
        for x1,y1,x2,y2 in lines[0]:
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            
            if(angle >= 45 and angle <= 135 or angle <= -45 and angle >= -135 ):
                cv2.line(image,(x1,y1+450),(x2,y2+450),(0,255,0),2)
                            
    except:
        print("error")
        
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)
