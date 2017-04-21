# Import required libraries
import sys
import time
import RPi.GPIO as GPIO
import cv2
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
sleeptime=1
LEFT_Forward.start(0)
RIGHT_Forward.start(0) 


try:
    while (1):
        LEFT_Forward.ChangeDutyCycle(100)
        RIGHT_Forward.ChangeDutyCycle(15)
except KeyboardInterrupt:
    print("break")
    GPIO.cleanup()
    pass
GPIO.cleanup()
