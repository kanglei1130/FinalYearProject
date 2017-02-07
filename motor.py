# Import required libraries
import sys
import time
import RPi.GPIO as GPIO

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

RIGHT_Forward=GPIO.PWM(6, 50)
RIGHT_Backward=GPIO.PWM(5, 50)

LEFT_Forward=GPIO.PWM(22, 50)
LEFT_Backward=GPIO.PWM(27, 50)
sleeptime=1

def forward(x):
    LEFT_Forward.start(50)
    RIGHT_Forward.start(50) 
    time.sleep(x)
    LEFT_Forward.stop(50)
    RIGHT_Forward.stop(50)
    time.sleep(.5)

def reverse(x):
    LEFT_Backward.start(50)
    RIGHT_Backward.start(50) 
    time.sleep(x)
    LEFT_Backward.stop(50)
    RIGHT_Backward.stop(50)
    time.sleep(.5)

    
def left(x):
    LEFT_Backward.start(50)
    RIGHT_Forward.start(50) 
    time.sleep(x)
    LEFT_Backward.stop(50)
    RIGHT_Forward.stop(50)
    time.sleep(.5)

    
def right(x):
    LEFT_Forward.start(50)
    RIGHT_Backward.start(50) 
    time.sleep(x)
    LEFT_Forward.stop(50)
    RIGHT_Backward.stop(50)
    time.sleep(.5)

while (1):
    forward(.3)
    left(.5)
    right(.9)
    left(.5)
GPIO.cleanup()
