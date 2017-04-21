from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import RPi.GPIO as GPIO
import numpy as np
import sys
import math

camera = PiCamera()
#camera.framerate = 60
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.5)
font = cv2.FONT_HERSHEY_SIMPLEX
Left_CAVG=[]
Left_MAVG=[]
Right_CAVG=[]
Right_MAVG=[]
RAVG_OLD = 1
LAVG_OLD = 1
LC_OLD = 1
LM_OLD = 1
RC_OLD = 1
RM_OLD = 1

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

RIGHT_Forward=GPIO.PWM(5, 100)
RIGHT_Backward=GPIO.PWM(6, 100)

LEFT_Forward=GPIO.PWM(27, 100)
LEFT_Backward=GPIO.PWM(22, 100)


def drive(l,r):
    LEFT_Forward.start(l)
    RIGHT_Forward.start(r) 
    time.sleep(.5)
    LEFT_Forward.stop(l)
    RIGHT_Forward.stop(r)
    


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  
    image = frame.array


    LROI = image[330:480,0:200]
    RROI = image[330:480,440:640]
    
    cv2.normalize(LROI,LROI,0,255,cv2.NORM_MINMAX)
    cv2.normalize(RROI,RROI,0,255,cv2.NORM_MINMAX)
    
    Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)
    Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)
    
    Rgray = cv2.cvtColor(RROI,cv2.COLOR_BGR2GRAY)
    Redges = cv2.Canny(Rgray,100,200,apertureSize = 3)
    
    Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,9,10,20)
    Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,9,10,20)
    
    cv2.rectangle(image,(0,330),(200,480),(0,0,255),2)
    cv2.rectangle(image,(440,330),(640,480),(0,0,255),2)
    cv2.line(image,(320,300),(320,480),(255,0,0),2)


    try:
        LAVGT = 0
        for x1,y1,x2,y2 in Llines[0]:
            
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            if(angle >= 45 and angle <= 135 or angle <= -45 and angle >= -135 ):
                cv2.line(image,(x1,y1+330),(x2,y2+330),(0,255,0),2)
                if float(x2-x1) == 0:
                    x1 = 0.001
                    x2 = 0.002
                LM =(float(y2-y1)/float(x2-x1))
                LC = y1 - (LM * x1)
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


    try:
        RAVGT = 0
        for x1,y1,x2,y2 in Rlines[0]:

            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            if(angle >= 45 and angle <= 135 or angle <= -45 and angle >= -135 ):
                cv2.line(image,(x1+440,y1+330),(x2+440,y2+330),(0,255,0),2)
                if float(x2-x1) == 0:
                    x1 = 0.001
                    x2 = 0.002
                RM=(float(y2-y1)/float(x2-x1))
                RC= y1 - (RM * x1) 
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
        
    diff =int(LAVG)+int(RAVG)
    
    cv2.putText(image,str(diff),(280,370), font, 1,(0,255,255),2)
    cv2.line(image,(320+diff,380),(320+diff,420),(0,255,0),1)

    cv2.putText(image,str(int(LAVG)),(100,320), font, 1,(0,255,0),2)
    cv2.putText(image,str(int(RAVG)),(500,320), font, 1,(0,255,0),2)
        
    cv2.imshow("Frame", image)
    time.sleep(.1)
    if diff <=50 and diff >= -50:
        print("Forward")
        drive(20,20)

    if diff >=100:
        print("Right")
        drive(10,20)
        

    if diff <=-100:
        print("Left")
        drive(20,10)
        


    GPIO.cleanup()
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

