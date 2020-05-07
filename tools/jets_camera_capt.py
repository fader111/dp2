#!/usr/bin/env python3
""" JETSON NANO With web interface based on flask with good quality picture 
"""
import jetson.inference
import jetson.utils
from threading import Timer, Thread, Lock
from multiprocessing.dummy import Process, Queue
import numpy as np
import time
import cv2
import sys
import os
import math



vis = True # xMode with Display

q_pict = Queue(maxsize=5)  # queue for web picts
q_status = Queue(maxsize=5) # queue for web status

width = 1280 #1280 # For Logitech 270 #640 # 
height = 720 #960 #480
#camera = '/dev/video0'
# create the camera and display
camera = jetson.utils.gstCamera(width, height, '0')
# display = jetson.utils.glDisplay() # only if x active
# frame, width, height = camera.CaptureRGBA(zeroCopy = True)
# frame = jetson.utils.cudaToNumpy(frame, width, height, 4)
    
# frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGBA2BGR)
    



while True: # 30 ms per frame in circle - too much..
    ts = time.time()
    frame, width, height = camera.CaptureRGBA(zeroCopy = False)

#    jetson.utils.cudaDeviceSynchronize()
    # create a numpy ndarray that references the CUDA memory
    # it won't be copied, but uses the same memory underneath
#    frame = jetson.utils.cudaToNumpy(frame, width, height, 4)
    #print ("img shape {}".format (aimg1.shape))
    
 #   frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGBA2BGR)
    time_str = f'{(time.time()-ts)*1000:.4} msec/frm'
    print(time_str)
#    cv2.putText(frame, time_str, (15, 15), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255,255,255), 1)
#    cv2.imshow("Frame", frame)
#    key = cv2.waitKey(0) & 0xFF
    # if the `q` key was pressed, break from the loop
#    if key == 27:
#        break
    

cv2.destroyAllWindows()
# camera.release()
#vs.stop()
