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
i = 655;
#camera.color_effects = (128,128)


LEFT_cascade = cv2.CascadeClassifier('LEFT_CASCADE_1.xml')
RIGHT_cascade = cv2.CascadeClassifier('RIGHT_CASCADE_1.xml')
STOP_cascade = cv2.CascadeClassifier('STOP_CASCADE_1.xml')
TRAFFIC_cascade = cv2.CascadeClassifier('TRAFFIC_CASCADE_3_STAGES.xml')



time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    image = image[80:440,0:640]
    STOP = STOP_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=10)    
    LEFT = LEFT_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=10)
    RIGHT = RIGHT_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=10)
    TRAFFIC = TRAFFIC_cascade.detectMultiScale(image,scaleFactor=1.2,minNeighbors=10)

    for (x,y,w,h) in LEFT:
        i+=1
        print 'Left FP detected.png Saved!... waiting 2 seconds'
        cv2.imwrite('BG_FP/FP_'+ str(i) +'.png',image)
        #cv2.putText(image,'LEFT',(x,y-10), font, 1,(0,255,0))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0),2)
        time.sleep(2)
                   
    for (x,y,w,h) in RIGHT:
        i+=1
        print 'Right FP detected.png Saved!... waiting 2 seconds'
        cv2.imwrite('BG_FP/FP_'+ str(i) +'.png',image)
        #cv2.putText(image,'RIGHT',(x,y-10), font, 1,(255,0,0))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (255,0,0),2)
        time.sleep(2)
                   
    for (x,y,w,h) in STOP:
        i+=1
        print 'Stop FP detected.png Saved!... waiting 2 seconds'
        cv2.imwrite('BG_FP/FP_'+ str(i) +'.png',image)
        #cv2.putText(image,'STOP',(x,y-10), font, 1,(0,0,255))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,255),2)
        time.sleep(2)

    for (x,y,w,h) in TRAFFIC:
        i+=1
        print 'Traffic FP detected.png Saved!... waiting 2 seconds'
        cv2.imwrite('BG_FP/FP_'+ str(i) +'.png',image)
        #cv2.putText(image,'STOP',(x,y-10), font, 1,(0,0,255))
        #cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,255),2)
        time.sleep(2)

    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

