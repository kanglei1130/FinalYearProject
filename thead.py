from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import cv2



# initialize the camera and stream
camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
stream = camera.capture_continuous(rawCapture, format="bgr",use_video_port=True)



# do a bit of cleanup
cv2.destroyAllWindows()
stream.close()
rawCapture.close()
camera.close()

# created a *threaded *video stream, allow the camera sensor to warmup,
# and start the FPS counter
vs = PiVideoStream().start()
time.sleep(2.0)

# loop over some frames...this time using the threaded stream
while(1):
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixel 
	frame = vs.read()
	
	frame= imutils.resize(frame,width=640)
	

	
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
