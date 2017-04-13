from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import sys
import math
from pykalman import KalmanFilter

camera = PiCamera()
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


# specify parameters
random_state = np.random.RandomState(0)
transition_matrix = [[1, 0.1], [0, 1]]
transition_offset = [-0.1, 0.1]
observation_matrix = np.eye(2) + random_state.randn(2, 2) * 0.1
observation_offset = [1.0, -1.0]
transition_covariance = np.eye(2)
observation_covariance = np.eye(2) + random_state.randn(2, 2) * 0.1
initial_state_mean = [5, -5]
initial_state_covariance = [[1, 0.1], [-0.1, 1]]

# sample from model
kf = KalmanFilter(
    transition_matrix, observation_matrix, transition_covariance,
    observation_covariance, transition_offset, observation_offset,
    initial_state_mean, initial_state_covariance,
    random_state=random_state
)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  
    image = frame.array


    LROI = image[380:480,50:200]
    RROI = image[380:480,440:590]
    cv2.normalize(LROI,LROI,0,255,cv2.NORM_MINMAX)
    cv2.normalize(RROI,RROI,0,255,cv2.NORM_MINMAX)
    
    Lgray = cv2.cvtColor(LROI,cv2.COLOR_BGR2GRAY)
    Ledges = cv2.Canny(Lgray,100,200,apertureSize = 3)
    
    Rgray = cv2.cvtColor(RROI,cv2.COLOR_BGR2GRAY)
    Redges = cv2.Canny(Rgray,100,200,apertureSize = 3)
    
    Llines = cv2.HoughLinesP(Ledges,1,np.pi/180,10,12,25)
    Rlines = cv2.HoughLinesP(Redges,1,np.pi/180,10,12,25)
    
    cv2.rectangle(image,(50,380),(200,480),(0,0,255),2)
    cv2.rectangle(image,(440,380),(590,480),(0,0,255),2)
    cv2.line(image,(320,300),(320,480),(255,0,0),2)


    try:
        LAVGT = 0
        for x1,y1,x2,y2 in Llines[0]:
             
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            if(angle >= 45 and angle <= 135 or angle <= -45 and angle >= -135 ):
                cv2.line(image,(x1+50,y1+380),(x2+50,y2+380),(0,255,0),2)
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

        LX = (100 - LC) / LM

        LAVG = LX-150
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
                cv2.line(image,(x1+440,y1+380),(x2+440,y2+380),(0,255,0),2)
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
            
        RX = (100 - RC) / RM
        RAVG = RX
        RAVG_OLD = RAVG
        RC_OLD = RC
        RM_OLD = RM
        Right_MAVG=[]
        Right_CAVG=[]

    except:
        RAVG = RAVG_OLD
    diff =int(LAVG)+int(RAVG)
    diff2 = diff
    diff3 = diff
    states, diff = kf.sample(
        n_timesteps=50,
        initial_state=initial_state_mean
    )
    filtered_state_estimates = kf.filter(diff2)
    smoothed_state_estimates = kf.smooth(diff3)
    
    cv2.putText(image,str(diff),(280,370), font, 1,(0,255,255),2)
    cv2.line(image,(320+diff,380),(320+diff,420),(0,255,0),1)

    #cv2.putText(image,str(diff2),(280,320), font, 1,(0,255,255),2)
    #cv2.line(image,(320+diff2,380),(320+diff2,420),(0,255,0),1)    
    
    cv2.putText(image,str(int(LAVG)),(100,360), font, 1,(0,255,0),2)
    cv2.putText(image,str(int(RAVG)),(500,360), font, 1,(0,255,0),2)
        
    cv2.imshow("Frame", image)
##    cv2.imshow("L", Ledges)
##    cv2.imshow("R", Redges)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

