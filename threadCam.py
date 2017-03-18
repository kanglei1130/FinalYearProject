# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

import imutils
import time
import cv2

class PiVideoStream:
        def __init__(self, resolution=(640, 480), framerate=32):
                print("Init")
                # initialize the camera and stream
                self.camera = PiCamera()
                self.camera.resolution = resolution
                self.camera.framerate = framerate
                self.rawCapture = PiRGBArray(self.camera, size=resolution)
                self.stream = self.camera.capture_continuous(self.rawCapture,
                        format="bgr", use_video_port=True)
        
        def start(self):
                # start the thread to read frames from the video stream
                print("Start")
                Thread(target=self.update, args=()).start()
                return self
 
        def update(self):
                # keep looping infinitely until the thread is stopped
                for f in self.stream:
                        # grab the frame from the stream and clear the stream in
                        # preparation for the next frame
                        self.frame = f.array
                        self.rawCapture.truncate(0)
                        return self.frame

class detect:
        def start(self, array):
                print("detect")

                STOP = STOP_cascade.detectMultiScale(array,scaleFactor=1.1,minNeighbors=10)    
                LEFT = LEFT_cascade.detectMultiScale(array,scaleFactor=1.1,minNeighbors=10)
                RIGHT = RIGHT_cascade.detectMultiScale(array,scaleFactor=1.1,minNeighbors=10)
                TRAFFIC = TRAFFIC_cascade.detectMultiScale(array,scaleFactor=1.1,minNeighbors=10)

                for (x,y,w,h) in LEFT:
                        cv2.putText(array,'LEFT',(x,y-10), font, 1,(0,255,0))
                        cv2.rectangle(array, (x,y), (x+w, y+h), (0,255,0),2)
            
                for (x,y,w,h) in RIGHT:
                        cv2.putText(array,'RIGHT',(x,y-10), font, 1,(255,0,0))
                        cv2.rectangle(array, (x,y), (x+w, y+h), (255,0,0),2)
                
                for (x,y,w,h) in STOP:
                        cv2.putText(array,'STOP',(x,y-10), font, 1,(0,0,255))
                        cv2.rectangle(array, (x,y), (x+w, y+h), (0,0,255),2)

                for (x,y,w,h) in TRAFFIC:
                        cv2.putText(array,'TRAFFIC',(x,y-10), font, 1,(0,255,255))
                        cv2.rectangle(array, (x,y), (x+w, y+h), (0,255,255),2)
                self.frame = array
                return self.frame

font = cv2.FONT_HERSHEY_SIMPLEX
LEFT_cascade = cv2.CascadeClassifier('LEFT_CASCADE.xml')
RIGHT_cascade = cv2.CascadeClassifier('RIGHT_CASCADE.xml')
STOP_cascade = cv2.CascadeClassifier('STOP_CASCADE.xml')
TRAFFIC_cascade = cv2.CascadeClassifier('TRAFFIC_CASCADE_3_STAGES.xml')

streamThread = PiVideoStream().start()
time.sleep(1.0)
detectThread = detect().start(streamThread.update())
time.sleep(1.0)


 
while 1:
        frame = streamThread.update()
        frame = detectThread.start(streamThread.update())
        image = frame
        image = image[80:440,0:640]

        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF



cv2.destroyAllWindows()
streamThread.stop()
