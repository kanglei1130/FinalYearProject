# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import RPi.GPIO as GPIO
import imutils
import time
import cv2
import numpy as np
import math
camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
font = cv2.FONT_HERSHEY_SIMPLEX
stop_flag = 0
left_flag = 0
right_flag = 0
LEFT_cascade = cv2.CascadeClassifier('Left_3.xml')
RIGHT_cascade = cv2.CascadeClassifier('Right3.xml')
STOP_cascade = cv2.CascadeClassifier('Stop_3.xml')
TRAFFIC_cascade = cv2.CascadeClassifier('Traffic_3.xml')


GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

RIGHT_Forward=GPIO.PWM(5, 1000)
RIGHT_Backward=GPIO.PWM(6, 1000)

LEFT_Forward=GPIO.PWM(27, 1000)
LEFT_Backward=GPIO.PWM(22, 1000)

LEFT_Forward.start(0)
RIGHT_Forward.start(0)
LEFT_Backward.start(0)
RIGHT_Backward.start(0)

def forward():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(20)
    RIGHT_Forward.ChangeDutyCycle(20)
    
def right():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(15)
    RIGHT_Forward.ChangeDutyCycle(25)

def left():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(25)
    RIGHT_Forward.ChangeDutyCycle(15)
    
def right2():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(15)
    RIGHT_Forward.ChangeDutyCycle(35)

def left2():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(35)
    RIGHT_Forward.ChangeDutyCycle(15)


def right3():
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    LEFT_Backward.start(0) 
    RIGHT_Forward.start(0) 
    LEFT_Backward.ChangeDutyCycle(15)
    RIGHT_Forward.ChangeDutyCycle(30)

def left3():
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.start(0)
    LEFT_Forward.start(0)
    RIGHT_Backward.ChangeDutyCycle(15)
    LEFT_Forward.ChangeDutyCycle(30)


def right_sign():
    print ("Right sign action")
    stop()
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    LEFT_Backward.start(0) 
    RIGHT_Forward.start(0) 
    LEFT_Backward.ChangeDutyCycle(50)
    RIGHT_Forward.ChangeDutyCycle(50)
    #time.sleep(2)
    LEFT_Backward.ChangeDutyCycle(0)
    RIGHT_Forward.ChangeDutyCycle(0)
    right_flag = 0
    
def left_sign():
    print ("left sign action")
    stop()
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.start(0)
    LEFT_Forward.start(0)
    RIGHT_Backward.ChangeDutyCycle(50)
    LEFT_Forward.ChangeDutyCycle(50)
    #time.sleep(2)
    RIGHT_Backward.ChangeDutyCycle(0)
    LEFT_Forward.ChangeDutyCycle(0)
    left_flag = 0
    
def stop():
    #print ("Stop sign action")
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    #time.sleep(1)


def getStream():
        print("Start camera.")
        global SROI
        global LROI
        global RROI
        global RAVG
        global LAVG
        global leftFrameFlag
        global rightFrameFlag
        global stopFrameFlag
        global trafficFrameFlag
        global leftLaneFlag
        global rightLaneFlag
        RAVG = 1
        LAVG = -1
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                image = frame.array 
                SROI = np.copy(image[50:400,0:640])
                LROI = image[220:480,0:200]
                RROI = image[220:480,440:640]
                leftFrameFlag = 1
                rightFrameFlag = 1
                stopFrameFlag = 1
                trafficFrameFlag = 1
                diff = RAVG+LAVG
                if(diff != 0.0):
                        diff = int(diff)
                        print("Lane Diff: "diff)
                leftLaneFlag = 1
                rightLaneFlag = 1

                key = cv2.waitKey(1) & 0xFF
                rawCapture.truncate(0)
def Left():
        print("Start detecting signs: Left.")
        global leftFrameFlag
        global SROI
        while(1):
                if(leftFrameFlag == 1):
                        LEFT = LEFT_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)
                        for (x,y,w,h) in LEFT:
                            h=h*.95
                            h=int(h)
                            dist = (((3.04*71.5*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'LEFT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,0))
                                print('LEFT: '+str(int(dist))+"cm")
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,255,0),2)
                                cv2.imshow("Image", SROI) 
                                if dist <= 25:
                                    left_flag =1
                        leftFrameFlag = 0;
def Right():
        print("Start detecting signs: Right.")
        global rightFrameFlag
        global SROI
        while(1):
                if(rightFrameFlag == 1):
                        RIGHT = RIGHT_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)
                        for (x,y,w,h) in RIGHT:
                            dist = (((3.04*70.5*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'RIGHT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(255,0,0))
                                print('RIGHT: '+str(int(dist))+"cm")
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (255,0,0),2)
                                if dist <= 25:
                                    right_flag =1
##                        cv2.imshow("Image", SROI)
                        rightFrameFlag = 0;


                
def Stop():
        print("Start detecting signs: Stop")
        i =1
        global stopFrameFlag
        global SROI
        while(1):
                if(stopFrameFlag == 1):
                        STOP = STOP_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)    
                        for (x,y,w,h) in STOP:
                            dist = (((3.04*65*480)/(h*2.76))-55)/10
                            if dist > 4 and dist < 40:
                                cv2.putText(SROI,'STOP: ' +str(int(dist))+"cm",(x,y+h+25), font, 1,(0,0,255))
                                print('STOP: '+str(int(dist))+"cm")
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,0,255),2)
                                stopimg = SROI
                                if dist <= 25:
                                    stop_flag =1
                        
                        #cv2.imshow("Image", stopimg)
                        stopFrameFlag = 0;


def Traffic():
        print("Start detecting signs: Traffic")
        global trafficFrameFlag
        global SROI
        while(1):
                if(trafficFrameFlag == 1):
                        TRAFFIC = TRAFFIC_cascade.detectMultiScale(SROI,scaleFactor=1.05,minNeighbors=10)             
                        for (x,y,w,h) in TRAFFIC:
                            h=h*1.08
                            h=int(h)
                            y=y-((h*1.05)-h)
                            y=int(y)
                            y2 = int(y+h/2)
                            dist = (((3.04*61*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'TRAFFIC: ' +str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,255))
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (255,0,0),2)
                                cv2.line(SROI,(x,y2),((x+w),y2), (255,0,0),2)
                                trafficROI = SROI[y:(y+h),x:(x+w)]
                                image2 = cv2.cvtColor(trafficROI,  cv2.COLOR_BGR2GRAY)
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image2)
                                px = max_loc[0]+x
                                py = max_loc[1]+y
                                if max_val > 250 and py < y2:      
                                        print('Traffic light Red: '+str(int(dist))+"cm")
                                        cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,0,255),2)
                                        cv2.line(SROI,(x,y2),((x+w),y2), (0,0,255),2)
                                        cv2.circle(SROI, (px,py), 10, (0, 0, 255), 2)
                                    
                                if max_val > 250 and py > y2:
                                        print('Traffic light Green: '+str(int(dist))+"cm")
                                        cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,255,0),2)
                                        cv2.line(SROI,(x,y2),((x+w),y2), (0,255,0),2)
                                        cv2.circle(SROI, (px,py), 10, (0, 255, 0), 2)
                                if max_val <= 250:   
                                        print('Traffic light off: '+str(int(dist))+"cm")

##                        cv2.imshow("Image", SROI)
                        trafficFrameFlag = 0;



def leftLane():
        print("Start lane sensing.")
        global leftLaneFlag
        global LAVG
        Left_CAVG=[]
        Left_MAVG=[]
        LAVG_OLD = 1 
        LC_OLD = 1
        LM_OLD = 1
        while(1):
                if(leftLaneFlag == 1):
                        cv2.normalize(LROI,LROI,0,255,cv2.NORM_MINMAX)
                        Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)
                        Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)
                        Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,5,6,15)
                        
                        try:
                            LAVGT = 0
                            
                            for x1,y1,x2,y2 in Llines[0]:
                                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                                if(angle >= 20 and angle <= 160 or angle <= -20 and angle >= -160 ):                                     
                                    cv2.line(LROI,(x1,y1),(x2,y2),(0,255,0),2)
                                    cv2.line(LROI,(x1,y1),(x1-32,y1),(0,0,255),2)
                                    cv2.line(LROI,(x1-32,y1),(x2-32,y2),(0,0,255),2)
                                    cv2.line(LROI,(x2,y2),(x2-32,y2),(0,0,255),2)
                                    if float(x2-x1) == 0:
                                        x1 = 0.001
                                        x2 = 0.002
                                    LM =(float(y2-y1)/float(x2-x1))
                                    LC = y1 - (LM * x1)
                                    LM2 =(float((y2)-(y1))/float(x2-x1))
                                    LC2 = y1 - (LM2 * x1)
                                    
                                    accum = []
                                    for YI in range((y2),(y1),1):
                                        X=int((YI-LC2)/LM2)
                                        
                                        for XI in range (X-30, X):
                                            if XI >=0:
                                                accum.append(LROI[YI,XI])           
                                    accum = np.mean(accum)
                                    if accum > 150:
                                        cv2.line(LROI,(x1,y1),(x1-32,y1),(0,255,0),2)
                                        cv2.line(LROI,(x1-32,y1),(x2-32,y2),(0,255,0),2)
                                        cv2.line(LROI,(x2,y2),(x2-32,y2),(0,255,0),2)
                                        Left_CAVG.append(LC)
                                        Left_MAVG.append(LM)
                            
                            LC = np.mean(Left_CAVG)
                            LM = np.mean(Left_MAVG)
                            if math.isnan(LM) == 1:
                                LM = LM_OLD
                            if math.isnan(LC) == 1:
                                LC = LC_OLD
                            LX = (150 - LC) / LM
                            LAVG = LX-200
                            LAVG_OLD = LAVG
                            LC_OLD = LC
                            LM_OLD = LM
                            Left_CAVG =[]
                            Left_MAVG =[]
                            
                        except:
                            LAVG = LAVG_OLD
                        cv2.putText(LROI,str(int(LAVG)),(100,200), font, 1,(255,255,0),2)  
                        cv2.imshow("Left", LROI)
                        leftLaneFlag = 0;

                
def rightLane():
        print("Start lane sensing: Right")
        global rightLaneFlag
        global RAVG
        Right_CAVG=[]
        Right_MAVG=[]
        RAVG_OLD = 1
        RC_OLD = 1
        RM_OLD = 1
        while(1):
                if(rightLaneFlag == 1):

                        cv2.normalize(RROI,RROI,0,255,cv2.NORM_MINMAX)
                        Rgray = cv2.cvtColor(RROI,cv2.COLOR_BGR2GRAY)
                        Redges = cv2.Canny(Rgray,100,200,apertureSize = 3)
                        Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,10,6,30)
                      
                        try:
                            RAVGT = 0
                            for x1,y1,x2,y2 in Rlines[0]:

                                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                                if(angle >= 20 and angle <= 160 or angle <= -20 and angle >= -160 ):
                                    cv2.line(RROI,(x1,y1),(x2,y2),(0,255,0),2) 
                                    cv2.line(RROI,(x1,y1),(x1+32,y1),(0,0,255),2)
                                    cv2.line(RROI,(x1+32,y1),(x2+32,y2),(0,0,255),2)
                                    cv2.line(RROI,(x2,y2),(x2+32,y2),(0,0,255),2)
                                    if float(x2-x1) == 0:
                                        x1 = 0.001
                                        x2 = 0.002
                                    RM=(float(y2-y1)/float(x2-x1))
                                    RC= y1 - (RM * x1) 

                                    RM2 =(float((y2)-(y1))/float((x2)-(x1)))
                                    RC2 = y1 - (RM2 * (x1))
                                    accum2 = []
                                    
                                    for YI in range((y1),(y2),1):
                                        X=int((YI-RC2)/RM2)
                                        for XI in range (X, X+30):
                                            if XI <=199:
                                                accum2.append(RROI[YI,XI])
                                                
                                    accum2 = np.mean(accum2)
                                    if accum2 > 150:
                                        cv2.line(RROI,(x1,y1),(x1+32,y1),(0,255,0),2)
                                        cv2.line(RROI,(x1+32,y1),(x2+32,y2),(0,255,0),2)
                                        cv2.line(RROI,(x2,y2),(x2+32,y2),(0,255,0),2)
                                        Right_CAVG.append(RC)
                                        Right_MAVG.append(RM)
                                    
                            RC = np.mean(Right_CAVG)
                            RM = np.mean(Right_MAVG)
                            
                            if math.isnan(RM) == 1:
                                RM = RM_OLD
                            if math.isnan(RC) == 1:
                                RC = RC_OLD

                                
                            RX = (150 - RC) / RM
                            RAVG = RX
                            RAVG_OLD = RAVG
                            RC_OLD = RC
                            RM_OLD = RM
                            Right_MAVG=[]
                            Right_CAVG=[]

                        except:
                            RAVG = RAVG_OLD
                        cv2.putText(RROI,str(int(RAVG)),(10,200), font, 1,(255,255,0),2)                            
                        cv2.imshow("Right", RROI)
                        rightLaneFlag = 0;
                        
                        
getStream = Thread(target=getStream)
Left = Thread(target=Left)
Right = Thread(target=Right)
Stop = Thread(target=Stop)
Traffic = Thread(target=Traffic)
leftLane = Thread(target=leftLane)
rightLane = Thread(target=rightLane)

getStream.start()
time.sleep(2)
Left.start()
time.sleep(.5)
Right.start()
time.sleep(.5)
Stop.start()
time.sleep(.5)
Traffic.start()
time.sleep(.5)
leftLane.start()
time.sleep(.5)
rightLane.start()
