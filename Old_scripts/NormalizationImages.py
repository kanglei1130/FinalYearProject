import time
import cv2
import RPi.GPIO as GPIO
import numpy as np
import sys
import math
import glob
i=1;

string ="Norm/Norm_"
for file in glob.glob("*.png"):
    print (file)
    img = cv2.imread(file)
    cv2.normalize(img,img,0,255,cv2.NORM_MINMAX)
    cv2.imwrite(string+file,img)
    i=i+1
