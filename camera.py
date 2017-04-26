from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import sys

camera = PiCamera()
camera.resolution = (640, 480)
camera.crop = (0,0,0,0)
rawCapture = PiRGBArray(camera, size=(640, 480))
#camera.color_effects = (128,128)

LEFT_cascade = cv2.CascadeClassifier('Left_3.xml')
RIGHT_cascade = cv2.CascadeClassifier('Right3.xml')
STOP_cascade = cv2.CascadeClassifier('Traffic_3.xml')
TRAFFIC_cascade = cv2.CascadeClassifier('Traffic_3.xml')

time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    image = image[80:440,0:640]
    STOP = STOP_cascade.detectMultiScale(image,scaleFactor=1.1,minNeighbors=10)    
    LEFT = LEFT_cascade.detectMultiScale(image,scaleFactor=1.1,minNeighbors=10)
    RIGHT = RIGHT_cascade.detectMultiScale(image,scaleFactor=1.1,minNeighbors=10)
    TRAFFIC = TRAFFIC_cascade.detectMultiScale(image,scaleFactor=1.1,minNeighbors=10)

    for (x,y,w,h) in LEFT:
        dist = (((3.04*71.5*480)/(h*2.76))-55)/10
        cv2.putText(image,'LEFT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,0))
        cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0),2)
    
    for (x,y,w,h) in RIGHT:
        dist = (((3.04*71.5*480)/(h*2.76))-55)/10
        cv2.putText(image,'RIGHT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(255,0,0))
        cv2.rectangle(image, (x,y), (x+w, y+h), (255,0,0),2)
        
##    for (x,y,w,h) in STOP:
##        cv2.putText(image,'STOP: ' + str((w+h)/2),(x,y+h+25), font, 1,(0,0,255))
##        cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,255),2)

    for (x,y,w,h) in TRAFFIC:
        dist = (((3.04*58*480)/(h*2.76))-50)/10
        cv2.putText(image,'TRAFFIC: ' +str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,255))
        cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,255),2)


    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

