# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import Queue
import imutils
import time
import cv2
import numpy as np
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



def getStream():
        print("Start camera.")
        global image
        global flag
        global flag1
        global flag2
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                image = frame.array
                flag = 1
                flag1 = 1
                flag2 = 1
                key = cv2.waitKey(1) & 0xFF
                rawCapture.truncate(0)
def signs1():
        print("Start detecting signs1.")
        global flag
        while(1):
                if(flag == 1):
                        SROI = np.copy(image[50:400,0:640])
                        LEFT = LEFT_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)
                        RIGHT = RIGHT_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)
                        
                        for (x,y,w,h) in LEFT:
                            h=h*.95
                            h=int(h)
                            dist = (((3.04*71.5*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'LEFT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,0))
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,255,0),2)
                                if dist <= 25:
                                    left_flag =1
                                    
                        for (x,y,w,h) in RIGHT:
                            dist = (((3.04*70.5*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'RIGHT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(255,0,0))
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (255,0,0),2)
                                if dist <= 25:
                                    right_flag =1
                           
                        cv2.imshow("Signs1", SROI)
                        flag = 0;
                
def signs2():
        print("Start detecting signs2")
        i =1
        global flag1
        while(1):
                if(flag1 == 1):
                        SROI = np.copy(image[50:400,0:640])
                        STOP = STOP_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)    
                        TRAFFIC = TRAFFIC_cascade.detectMultiScale(SROI,scaleFactor=1.05,minNeighbors=10)
                                           
                        for (x,y,w,h) in STOP:
                            dist = (((3.04*65*480)/(h*2.76))-55)/10
                            if dist > 4 and dist < 40:
                                cv2.putText(SROI,'STOP: ' +str(int(dist))+"cm",(x,y+h+25), font, 1,(0,0,255))
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,0,255),2)
                                if dist <= 25:
                                    stop_flag =1
                          
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
                                    cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,0,255),2)
                                    cv2.line(SROI,(x,y2),((x+w),y2), (0,0,255),2)
                                    cv2.circle(SROI, (px,py), 10, (0, 0, 255), 2)
                                    
                                if max_val > 250 and py > y2:
                                    cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,255,0),2)
                                    cv2.line(SROI,(x,y2),((x+w),y2), (0,255,0),2)
                                    cv2.circle(SROI, (px,py), 10, (0, 255, 0), 2)                      
                        cv2.imshow("Signs2", SROI)
                        flag1 = 0;
def lane():
        print("Start lane sensing.")
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
        global image
        global flag2
        while(1):
                if(flag2 == 1):
                        LROI = np.copy(image[220:480,0:200])
                        RROI = np.copy(image[220:480,440:640])
                        cv2.normalize(LROI,LROI,0,255,cv2.NORM_MINMAX)
                        Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)
                        Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)
                        
                        cv2.normalize(RROI,RROI,0,255,cv2.NORM_MINMAX)
                        Rgray = cv2.cvtColor(RROI,cv2.COLOR_BGR2GRAY)
                        Redges = cv2.Canny(Rgray,100,200,apertureSize = 3)
                        
                        Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,5,6,15)
                        Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,10,6,30)


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
                                                accum.append(image[YI,XI])
                                                
                                    accum = np.mean(accum)
                                    if accum < 50:
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
                            #LAVG = -1000


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
                                    RC2 = y1 - (RM2 * (x1+440))
                                    accum2 = []
                                    
                                    for YI in range((y1),(y2),1):
                                        X=int((YI-RC2)/RM2)
                                        for XI in range (X, X+30):
                                            if XI >=0 and XI <=639:
                                                accum2.append(image[YI,XI])
                                                
                                    accum2 = np.mean(accum2)
                                    if accum2 < 50:
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
                            #RAVG = 2000
                            
##                        cv2.imshow("Left", LROI)
##                        cv2.imshow("Right", RROI)
                        flag2 = 0;
                        
                        
getStream = Thread(target=getStream)
signs1 = Thread(target=signs1)
signs2 = Thread(target=signs2)
lane = Thread(target=lane)
getStream.start()
time.sleep(2)
signs1.start()
time.sleep(.1)
signs2.start()
time.sleep(.1)
lane.start()

