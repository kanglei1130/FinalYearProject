# imports
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
camera = PiCamera()#Setup camera 
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
font = cv2.FONT_HERSHEY_SIMPLEX
LEFT_cascade = cv2.CascadeClassifier('Left_3.xml')#Point to cascade files for detections
RIGHT_cascade = cv2.CascadeClassifier('Right3.xml')
STOP_cascade = cv2.CascadeClassifier('Stop_3.xml')
TRAFFIC_cascade = cv2.CascadeClassifier('Traffic_3.xml')

GPIO.cleanup()#Setup Gpio pins
GPIO.setmode(GPIO.BCM)

GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

RIGHT_Forward=GPIO.PWM(5, 100)#Setup gpio as PWM 
RIGHT_Backward=GPIO.PWM(6, 100)

LEFT_Forward=GPIO.PWM(27, 100)
LEFT_Backward=GPIO.PWM(22, 100)

LEFT_Forward.start(0)#Start all with duty cycle of 0
RIGHT_Forward.start(0)
LEFT_Backward.start(0)
RIGHT_Backward.start(0)

def forward():#Function to drive forward uses no turn rate
    LEFT_Backward.stop()#Ensure any backward pins are stop and start forward pins again
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(20)
    RIGHT_Forward.ChangeDutyCycle(20)
    time.sleep(0.3)
    LEFT_Forward.ChangeDutyCycle(0)
    RIGHT_Forward.ChangeDutyCycle(0)
    
def right():#Functions to drive left and right 
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(20)
    RIGHT_Forward.ChangeDutyCycle(20+turnRate)#Add turn rate to duty cycle a number based off lane diff between 0 and 30
    time.sleep(0.3)#drive forward for .3 of a second
    LEFT_Forward.ChangeDutyCycle(0)#then turn off motors until next frame is processed
    RIGHT_Forward.ChangeDutyCycle(0)
    

def left():
    LEFT_Backward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.start(0)
    RIGHT_Forward.start(0) 
    LEFT_Forward.ChangeDutyCycle(20+turnRate)
    RIGHT_Forward.ChangeDutyCycle(20)
    time.sleep(0.3)
    LEFT_Forward.ChangeDutyCycle(0)
    RIGHT_Forward.ChangeDutyCycle(0)
    

def right_sign():#Function for when a right sign is detected
    print ("Right sign action")
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    LEFT_Backward.start(0) 
    RIGHT_Forward.start(0) 
    LEFT_Backward.ChangeDutyCycle(30)
    RIGHT_Forward.ChangeDutyCycle(30)
    time.sleep(1)
    LEFT_Backward.ChangeDutyCycle(0)
    RIGHT_Forward.ChangeDutyCycle(0)
    
def left_sign():#Function for when a left sign is detected
    print ("left sign action")
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.start(0)
    LEFT_Forward.start(0)
    RIGHT_Backward.ChangeDutyCycle(30)
    LEFT_Forward.ChangeDutyCycle(30)
    time.sleep(1)
    RIGHT_Backward.ChangeDutyCycle(0)
    LEFT_Forward.ChangeDutyCycle(0)
    
def stop():
    print ("Stop sign action")#Function for when a stop sign or red traffic light is detected
    LEFT_Backward.stop()
    RIGHT_Forward.stop()
    RIGHT_Backward.stop()
    LEFT_Forward.stop()
    time.sleep(1)
    
def getStream():#thread to get camera stream but it also does motor control now
        print("Start camera.")
        global SROI#GLobals declared for use in other threads
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
        global stop_flag
        global left_flag 
        global right_flag
        global trafficRedFlag
        global turnRate
        RAVG = 0#Some initial values that get filled by other threads later
        LAVG = 0
        stop_flag = 0#Flags to keep everything in sync
        left_flag = 0
        right_flag = 0
        rightFrameFlag = 0
        leftFrameFlag = 0
        stopFrameFlag = 0
        leftLaneFlag = 0
        rightLaneFlag = 0
        trafficFrameFlag = 0
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):#continious loop to get frames from camera
            if(stopFrameFlag == 0 and rightFrameFlag==0 and leftFrameFlag == 0 and trafficFrameFlag == 0 and leftLaneFlag == 0 and rightLaneFlag == 0):#Make sure that all threads have run
                    image = frame.array
                    SROI = np.copy(image[50:400,0:640])#Setup region of interest for sign detection 630*350 instead of 640*480 from the camera
                    LROI = image[220:480,0:200]#Setup region of interest for lane detection left and right 200*260
                    RROI = image[220:480,440:640]

                    if RAVG == 0:#When no lane is detected on either side set RAVG or LAVG to large number (but not too large) to help correct itself 
                            RAVG = 270
                    if LAVG == 0:
                            LAVG = -270
                    diff = RAVG+LAVG#Calculate Diff
                    if(diff != 0.0):
                            diff = int(diff)
                            print("Lane Diff: "+str(diff))
                            
                            if stop_flag == 1:#Check for road sign flags to be raised and excute the corrisponding flag
                                    stop()
                            if left_flag == 1:
                                    left_sign()
                            if right_flag == 1:
                                    right_sign()
                            if trafficRedFlag == 1:
                                    stop()
                                    
                            if (stop_flag == 0 and left_flag == 0 and right_flag == 0 and trafficRedFlag == 0):#Check again that no sign flags are high before doing motor control
                                    absDiff =abs(diff)#get the absloute value of diff
                                    m = 0.05#a number to calculate turn rate with higher numbers = more agressive correction  
                                    turnRate = m*absDiff#get turn rate
                                    if turnRate > 30:#Limit turn rate incase of a bad detection 
                                            turnRate = 30
                                    if diff == 0:#Then check if diff is a positive or negative number and go left or right using the turn rate
                                            forward()
                                    elif diff < 0:
                                            left()
    ##                                        print("Left")
                                    elif diff > 0:
                                            right()
    ##                                        print("Right")

                                            

                    stop_flag = 0#Reset all the sign flags 
                    right_flag = 0
                    left_flag = 0
                    trafficRedFlag =0
                    leftFrameFlag = 1#Set the frame ready flags to high so threads can get the next frame
                    rightFrameFlag = 1
                    stopFrameFlag = 1
                    trafficFrameFlag = 1     
                    leftLaneFlag = 1
                    rightLaneFlag = 1

            key = cv2.waitKey(1) & 0xFF
            rawCapture.truncate(0)
def Left():
        print("Start detecing signs: Left.")
        global leftFrameFlag#Set globals that i need to modify here
        global left_flag
        global SROI
        while(1):#loop forever checking if frame flag has gone high 
                if(leftFrameFlag == 1):
                        LEFT = LEFT_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)#detect for left signs in SROI using scale factor(allows detection of larger objects then what was trained for) and higher minNeighbours = harder to detect but less FP
                        for (x,y,w,h) in LEFT:
                            h=h*.95#Adjust the bounding box as it was a tad to big 
                            h=int(h)#Convert to an int as it is a pixel location
                            #Calculate distance to object(camera focal length*object height*number of pixels in sensor high/height of detection*height of image sensor)-offset from camera to nose of car
                            dist = (((3.04*71.5*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:#ignore anything less then 7cm and greater then 40cm away
                                cv2.putText(SROI,'LEFT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,0))#draw on the roi "left cm"
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,255,0),2)#and put a rectangel around the detection
                                print('LEFT: '+str(int(dist))+"cm")#Print how far the detection is to the console thingy
                                if dist <= 20:
                                    left_flag =1#If distance is <20 cm then rais a flag so the corrisponding command is called up in motor control area
                        leftFrameFlag = 0;#Change this flag to zero because we have used the current frame
                        
def Right():#Same as above
        print("Start detecting signs: Right.")
        global rightFrameFlag
        global right_flag
        global SROI
        while(1):
                if(rightFrameFlag == 1):
                        RIGHT = RIGHT_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)
                        for (x,y,w,h) in RIGHT:
                            dist = (((3.04*70.5*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'RIGHT: '+str(int(dist))+"cm",(x,y+h+25), font, 1,(255,0,0))
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (255,0,0),2)
                                print('RIGHT: '+str(int(dist))+"cm")
                                if dist <= 20:
                                    right_flag =1
##                        cv2.imshow("Image", SROI)
                        rightFrameFlag = 0;


                
def Stop():
        print("Start detecting signs: Stop")
        global stopFrameFlag
        global stop_flag
        global SROI
        while(1):
                if(stopFrameFlag == 1):
                        STOP = STOP_cascade.detectMultiScale(SROI,scaleFactor=1.1,minNeighbors=10)    
                        for (x,y,w,h) in STOP:
                            dist = (((3.04*65*480)/(h*2.76))-55)/10
                            if dist > 4 and dist < 25: 
                                cv2.putText(SROI,'STOP: ' +str(int(dist))+"cm",(x,y+h+25), font, 1,(0,0,255))
                                print('STOP: '+str(int(dist))+"cm")
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,0,255),2)
                                stopimg = SROI                             
                                if dist <= 25:
                                    stop_flag =1                                
##                        cv2.imshow("Image", stopimg)
                        stopFrameFlag = 0;


def Traffic():
        print("Start detecting signs: Traffic")
        global trafficFrameFlag
        global SROI
        global trafficRedFlag
        while(1):
                if(trafficFrameFlag == 1):
                        TRAFFIC = TRAFFIC_cascade.detectMultiScale(SROI,scaleFactor=1.05,minNeighbors=10)             
                        for (x,y,w,h) in TRAFFIC:
                            h=h*1.08
                            h=int(h)
                            y=y-((h*1.05)-h)
                            y=int(y)
                            y2 = int(y+h/2)#Get a half way point of the bounding box
                            dist = (((3.04*61*480)/(h*2.76))-55)/10
                            if dist > 7 and dist < 40:
                                cv2.putText(SROI,'TRAFFIC: ' +str(int(dist))+"cm",(x,y+h+25), font, 1,(0,255,255))
                                cv2.rectangle(SROI, (x,y), (x+w, y+h), (255,0,0),2)
                                cv2.line(SROI,(x,y2),((x+w),y2), (255,0,0),2)
                                trafficROI = SROI[y:(y+h),x:(x+w)]#Create a new Region of interest within the detection box 
                                image2 = cv2.cvtColor(trafficROI,  cv2.COLOR_BGR2GRAY)#Conver to grayscale
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image2)#Get the maxLoc (brightest point in the ROI) and maxVal(Value of brightest point)
                                px = max_loc[0]+x#Get coordinates of the brightest spot
                                py = max_loc[1]+y
                                if max_val > 250 and py < y2:#Check that max val has saturated the camera (well close to saturation) and check if the y value is in the top half of the bounding box  
                                        print('Traffic light Red: '+str(int(dist))+"cm")
                                        cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,0,255),2)#Change box color to red because it looks nice
                                        cv2.line(SROI,(x,y2),((x+w),y2), (0,0,255),2)
                                        cv2.circle(SROI, (px,py), 10, (0, 0, 255), 2)#Draw a circle around the brightest spo
                                        if dist < 25:
                                            trafficRedFlag = 1#Set traffic light red flag to 1
                                if max_val > 250 and py > y2:#samesies for green except brightest spot must be in lower half
                                        print('Traffic light Green: '+str(int(dist))+"cm")
                                        cv2.rectangle(SROI, (x,y), (x+w, y+h), (0,255,0),2)
                                        cv2.line(SROI,(x,y2),((x+w),y2), (0,255,0),2)
                                        cv2.circle(SROI, (px,py), 10, (0, 255, 0), 2)
                                        
                                if max_val <= 250:   
                                        print('Traffic light off: '+str(int(dist))+"cm")#just print that the traffic light is off 

##                        cv2.imshow("Image", SROI)
                        trafficFrameFlag = 0;



def leftLane():
        print("Start lane sensing.")
        global leftLaneFlag#Globals that i will be modifying here 
        global LAVG
        Left_CAVG=[]#Some other variables i will be needeing later (probably)
        Left_MAVG=[]
        LAVG_OLD = 1 
        LC_OLD = 1
        LM_OLD = 1
        while(1):
                if(leftLaneFlag == 1):#Wait for frame flag
                        cv2.normalize(LROI,LROI,0,255,cv2.NORM_MINMAX)#Normalize the ROI helps with low light situations although it tends to add a bit of noise
                        Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)#Convert to gray because canny cannae work on a color image 
                        Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)#Get black and white canny edge detection
                        Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,5,4,20)#And detect lines from that image
                        try:#Try and catch just incase
                            i = 0
                            for x1,y1,x2,y2 in Llines[0]:#Loop all the lines detected
                                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi#Convert to a regular angle instead of x and y points
                                if(angle >= 20 and angle <= 160 or angle <= -20 and angle >= -160 ):#Reject horizontal angles                                      
                                    cv2.line(LROI,(x1,y1),(x2,y2),(0,255,0),2)#Draw detected line
                                    cv2.line(LROI,(x1,y1),(x1-32,y1),(0,0,255),2)#and draw a red box around it of width 32
                                    cv2.line(LROI,(x1-32,y1),(x2-32,y2),(0,0,255),2)
                                    cv2.line(LROI,(x2,y2),(x2-32,y2),(0,0,255),2)
                                    if float(x2-x1) == 0:#Check these are not 0 so i dont divide by zero later
                                        x1 = 0.001
                                        x2 = 0.002
                                    LM =(float(y2-y1)/float(x2-x1))#Get the slope of each line
                                    LC = y1 - (LM * x1) #Get the Y intersect value
                                    LM2 =(float((y2)-(y1))/float(x2-x1))#Get them again for a loop later
                                    LC2 = y1 - (LM2 * x1)
                                    
                                    accum = []#Clear array used to hold overall pixel value 
                                    for YI in range((y2),(y1),1):#For loop to loop each Y value in the box 
                                        X=int((YI-LC2)/LM2) #Get each x value along the line 
                                        
                                        for XI in range (X-30, X):#THen loop between x-30 and x (size of the box we are looking in )
                                            if XI >=0:#Check that im not out of the ROI
                                                accum.append(LROI[YI,XI])#append the pixel value of each pixel in the box to this list    
                                    accum = np.mean(accum)#Get the mean value of all the pixel values low numbers are dar high numbers are bright
##                                    if accum < 50:#For detecting black lines
                                    if accum > 120:#only get white lines
                                        cv2.line(LROI,(x1,y1),(x1-32,y1),(0,255,0),2)#Draw a green box as this is a good detection
                                        cv2.line(LROI,(x1-32,y1),(x2-32,y2),(0,255,0),2)
                                        cv2.line(LROI,(x2,y2),(x2-32,y2),(0,255,0),2)
                                        Left_CAVG.append(LC)#Keep these C and M values as they are good detections
                                        Left_MAVG.append(LM)
                                        i=i+1  #incrment counter to ensure calculations are only carried out if there is a detection                   
                            if i !=0 :
                                    LC = np.mean(Left_CAVG)#Get the average of any good lines
                                    LM = np.mean(Left_MAVG)
                                    LX = (150 - LC) / LM#Get the y intersect 
                                    LAVG = LX -200 #Add offset
                                    LAVG_OLD = LAVG#Set an old variable to the current one incase next frame has no detections(Not used any more but keeping this here incase i come back to it)
                                    LC_OLD = LC
                                    LM_OLD = LM
                                    Left_CAVG =[]#clear arrays
                                    Left_MAVG =[]
        
                            else:
                                    LAVG = -270#If nothing is detected set Lavg to -270 so the car corrects quickly
                        except:                         
                            LAVG = -271#If an exception is raised set LAVG to -271 for the same reason as above except i can see an exception has happend
                        cv2.putText(LROI,str(int(LAVG)),(100,200), font, 1,(255,255,0),2)#Put on the ROI the LAVG value
                          
                        cv2.imshow("Left", LROI)
                        leftLaneFlag = 0;

                
def rightLane():#Same as above more or less
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
                        Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,10,4,20)
                      
                        try:
                            RAVGT = 0
                            i = 0
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
##                                    if accum2 < 70:
                                    if accum2 > 120:
                                        cv2.line(RROI,(x1,y1),(x1+32,y1),(0,255,0),2)
                                        cv2.line(RROI,(x1+32,y1),(x2+32,y2),(0,255,0),2)
                                        cv2.line(RROI,(x2,y2),(x2+32,y2),(0,255,0),2)
                                        Right_CAVG.append(RC)
                                        Right_MAVG.append(RM)
                                        i=i+1                     
                            if i !=0 :
                                    RC = np.mean(Right_CAVG)
                                    RM = np.mean(Right_MAVG)
                                    RX = (150 - RC) / RM
                                    RAVG = RX
                                    RAVG_OLD = RAVG
                                    
                                    RC_OLD = RC
                                    RM_OLD = RM
                                    Right_CAVG =[]
                                    Right_MAVG =[]
        
                            else:
                                    RAVG = 270
                        except:
                            RAVG = 271
                            
                        cv2.putText(RROI,str(int(RAVG)),(10,200), font, 1,(255,255,0),2)                            
                        cv2.imshow("Right", RROI)
                        rightLaneFlag = 0;

#Back at main                   
getStream = Thread(target=getStream)#Set up functions as threads which are the bane of my life
Left = Thread(target=Left)
Right = Thread(target=Right)
Stop = Thread(target=Stop)
Traffic = Thread(target=Traffic)
leftLane = Thread(target=leftLane)
rightLane = Thread(target=rightLane)

getStream.start()#Start camera stream and wait for camera to warmup
time.sleep(2)
Left.start()#Start all the other functions with a bit of wait (starting them at the same time causes it to sometimes crash upon launch)
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
