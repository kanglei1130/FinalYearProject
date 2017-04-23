from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import RPi.GPIO as GPIO
import numpy as np
import sys
import math

camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
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
    
def left():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(15)
    RIGHT_Forward.ChangeDutyCycle(35)

def right():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(35)
    RIGHT_Forward.ChangeDutyCycle(15)
    
def left2():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(15)
    RIGHT_Forward.ChangeDutyCycle(40)

def right2():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(40)
    RIGHT_Forward.ChangeDutyCycle(15)


def left3():
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    LEFT_Backward.start(0) 
    RIGHT_Forward.start(0) 
    LEFT_Backward.ChangeDutyCycle(30)
    RIGHT_Forward.ChangeDutyCycle(30)

def right3():
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.start(0)
    LEFT_Forward.start(0)
    RIGHT_Backward.ChangeDutyCycle(30)
    LEFT_Forward.ChangeDutyCycle(30)


def left4():
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    LEFT_Backward.start(0) 
    RIGHT_Forward.start(0) 
    LEFT_Backward.ChangeDutyCycle(40)
    RIGHT_Forward.ChangeDutyCycle(50)

def right4():
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.ChangeDutyCycle(40)
    LEFT_Forward.ChangeDutyCycle(50)

    
def stop():
    LEFT_Forward.ChangeDutyCycle(0)
    RIGHT_Forward.ChangeDutyCycle(0)

try:
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
      
        image = frame.array


        LROI = image[220:480,0:200]
        RROI = image[220:480,440:640]
        
        cv2.normalize(LROI,LROI,0,255,cv2.NORM_MINMAX)
        cv2.normalize(RROI,RROI,0,255,cv2.NORM_MINMAX)
        
        Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)
        Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)
        
        Rgray = cv2.cvtColor(RROI,cv2.COLOR_BGR2GRAY)
        Redges = cv2.Canny(Rgray,100,200,apertureSize = 3)
        
        Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,5,6,15)
        Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,10,6,30)
        
        cv2.rectangle(image,(0,220),(200,480),(0,0,255),2)
        cv2.rectangle(image,(440,220),(640,480),(0,0,255),2)
        cv2.line(image,(320,300),(320,480),(255,0,0),2)


        try:
            LAVGT = 0
            
            for x1,y1,x2,y2 in Llines[0]:
                
                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                if(angle >= 20 and angle <= 160 or angle <= -20 and angle >= -160 ):
                    cv2.line(image,(x1,y1+220),(x2,y2+220),(0,255,0),2)
                    
                    cv2.line(image,(x1,y1+220),(x1-32,y1+220),(0,0,255),2)
                    cv2.line(image,(x1-32,y1+220),(x2-32,y2+220),(0,0,255),2)
                    cv2.line(image,(x2,y2+220),(x2-32,y2+220),(0,0,255),2)
                    if float(x2-x1) == 0:
                        x1 = 0.001
                        x2 = 0.002
                    LM =(float(y2-y1)/float(x2-x1))
                    LC = y1 - (LM * x1)
                    
                    LM2 =(float((y2+220)-(y1+220))/float(x2-x1))
                    LC2 = y1+220 - (LM2 * x1)
                    accum = []
                    
                    for YI in range((y2+220),(y1+220),1):
                        X=int((YI-LC2)/LM2)
                        
                        for XI in range (X-30, X):
                            if XI >=0:
                                accum.append(image[YI,XI])
                                
                    accum = np.mean(accum)
                    if accum < 80:
                        cv2.line(image,(x1,y1+220),(x1-32,y1+220),(0,255,0),2)
                        cv2.line(image,(x1-32,y1+220),(x2-32,y2+220),(0,255,0),2)
                        cv2.line(image,(x2,y2+220),(x2-32,y2+220),(0,255,0),2)
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
            #LAVG = -1000


        try:
            RAVGT = 0
            for x1,y1,x2,y2 in Rlines[0]:

                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                if(angle >= 20 and angle <= 160 or angle <= -20 and angle >= -160 ):
                    cv2.line(image,(x1+440,y1+220),(x2+440,y2+220),(0,255,0),2) 
                    cv2.line(image,(x1+440,y1+220),(x1+440+32,y1+220),(0,0,255),2)
                    cv2.line(image,(x1+440+32,y1+220),(x2+440+32,y2+220),(0,0,255),2)
                    cv2.line(image,(x2+440,y2+220),(x2+440+32,y2+220),(0,0,255),2)
                    if float(x2-x1) == 0:
                        x1 = 0.001
                        x2 = 0.002
                    RM=(float(y2-y1)/float(x2-x1))
                    RC= y1 - (RM * x1) 

                    RM2 =(float((y2+220)-(y1+220))/float((x2+440)-(x1+440)))
                    RC2 = y1+220 - (RM2 * (x1+440))
                    accum2 = []
                    
                    for YI in range((y1+220),(y2+220),1):
                        X=int((YI-RC2)/RM2)
                        for XI in range (X, X+30):
                            if XI >=0 and XI <=639:
                                accum2.append(image[YI,XI])
                                
                    accum2 = np.mean(accum2)
                    if accum2 < 80:
                        cv2.line(image,(x1+440,y1+220),(x1+440+32,y1+220),(0,255,0),2)
                        cv2.line(image,(x1+440+32,y1+220),(x2+440+32,y2+220),(0,255,0),2)
                        cv2.line(image,(x2+440,y2+220),(x2+440+32,y2+220),(0,255,0),2)
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
            #RAVG = 2000
            
        diff =int(LAVG)+int(RAVG)
        
        cv2.putText(image,str(diff),(280,370), font, 1,(0,255,255),2)
        cv2.line(image,(320+diff,380),(320+diff,420),(0,255,0),1)

        cv2.putText(image,str(int(LAVG)),(100,200), font, 1,(0,255,0),2)
        cv2.putText(image,str(int(RAVG)),(500,200), font, 1,(0,255,0),2)
            
        cv2.imshow("Frame", image)
        cv2.imshow("LEFT",Ledges)
        cv2.imshow("Right",Redges)
        if diff <=50 and diff >= -50:
            print("Forward")
            forward()

        if diff <=-51 and diff >=-100:
            print("Right")
            right()

        if diff >=51 and diff <=100:
            print("Left")
            left()
                
        if diff <=-101 and diff >= -149:
            print("Right2")
            right2()

        if diff >=101 and diff <=149:
            print("Left2")
            left2()

        if diff <=-150 and diff >= -199:
            print("Right3")
            right3()

        if diff >=150 and diff <=199:
            print("Left3")
            left3()
            
        if diff <=-200 and diff >= -999:
            print("Right4")
            right4()

        if diff >=200 and diff <=999:
            print("Left4")
            left4()

        if diff >= 1000:
            print("Stop")
            stop()
            
        if diff <= -1000:
            print("Stop")
            stop()

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
    
except KeyboardInterrupt:
    print("break")
    GPIO.cleanup()
    pass
