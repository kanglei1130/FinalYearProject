from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import sys

camera = PiCamera()
camera.resolution = (640, 480)
camera.crop = (0,0,0,0)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
i = 60;
j = 160;
k = 100;
#camera.color_effects = (128,128)

LEFT_cascade = cv2.CascadeClassifier('LEFT_CASCADE.xml')
RIGHT_cascade = cv2.CascadeClassifier('RIGHT_CASCADE.xml')
STOP_cascade = cv2.CascadeClassifier('STOP_CASCADE_995.xml')

time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    image = image[80:440,0:640]
    STOP = STOP_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=45)    
    LEFT = LEFT_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=20)
    RIGHT = RIGHT_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=20)

    for (x,y,w,h) in LEFT:
        i+=1
        print 'Left_'+ str(i) +'.png Saved!... waiting 5 seconds'
        cv2.imwrite('BG/Left_'+ str(i) +'.png',image)
        #cv2.putText(image,'LEFT',(x,y-10), font, 1,(0,255,0))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0),2)
        time.sleep(5)
                   
    for (x,y,w,h) in RIGHT:
        j+=1
        print 'Right_'+ str(j) +'.png Saved!... waiting 5 seconds'
        cv2.imwrite('BG/Right_'+ str(j) +'.png',image)
        #cv2.putText(image,'RIGHT',(x,y-10), font, 1,(255,0,0))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (255,0,0),2)
        time.sleep(5)
                   
    for (x,y,w,h) in STOP:
        k+=1
        print 'Stop_'+ str(k) +'.png Saved!... waiting 5 seconds'
        cv2.imwrite('BG/Stop__'+ str(k) +'.png',image)
        #cv2.putText(image,'STOP',(x,y-10), font, 1,(0,0,255))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,255),2)
        time.sleep(5)

    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

