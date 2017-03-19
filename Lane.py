from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import sys

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    
    image = frame.array
    LROI = image[420:480,50:200]
    RROI = image[420:480,440:590]
    
    Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)
    Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)
    
    Rgray = cv2.cvtColor(RROI,cv2.COLOR_BGR2GRAY)
    Redges = cv2.Canny(Rgray,100,200,apertureSize = 3)
    
    Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,5,10,2)
    Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,5,10,2)
    cv2.rectangle(image,(50,420),(200,480),(0,0,255),2)
    cv2.rectangle(image,(440,420),(590,480),(0,0,255),2)
    
    try:
        i=0
        LAVGT = 0
        for x1,y1,x2,y2 in Llines[0]:
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            if(angle >= 45 and angle <= 135 or angle <= -45 and angle >= -135 ):
                cv2.line(image,(x1+50,y1+420),(x2+50,y2+420),(0,255,0),2)
                LAVG = (x2+x1)/2
                i=i+1
                LAVGT = LAVGT + LAVG
            LAVGT = LAVGT/i
                          
    except:
        print("error")
        RAVG = 1
        LAVG = 1

    try:
        j=0
        RAVGT = 0
        for x1,y1,x2,y2 in Rlines[0]:
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            if(angle >= 45 and angle <= 135 or angle <= -45 and angle >= -135 ):
                cv2.line(image,(x1+440,y1+420),(x2+440,y2+420),(0,255,0),2)
                RAVG = (x1+x2)/2
                j=j+1
                RAVGT = RAVGT + RAVG
            RAVGT = RAVGT/i
                          
                        
    except:
        print("error")
    diff =RAVGT-LAVGT
    cv2.putText(image,str(diff),(230,400), font, 1,(0,0,0),2)
    if(diff <= 50 and diff >= -50):
        cv2.putText(image,("FORWARD"),(230,440), font, 1,(0,0,0),2)
    if(diff < -50):
        cv2.putText(image,("TURN RIGHT"),(230,440), font, 1,(0,0,0),2)
    if(diff > 50):
        cv2.putText(image,("TURN LEFT"),(230,440), font, 1,(0,0,0),2)
    
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)
