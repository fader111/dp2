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
import Jetson.GPIO as GPIO
import sys
import os
import math


GPIO.setwarnings(False) # suppresses GPIO warnings
GPIO.setmode(GPIO.BOARD)
GREEN = 40
GPIO.setup(GREEN, GPIO.OUT)
RED = 38
GPIO.setup(RED, GPIO.OUT)

vis = False # xMode with Display
memmon = False

q_pict = Queue(maxsize=5)  # queue for web picts
q_status = Queue(maxsize=5) # queue for web status

# jetson inference networks list
network_lst = [ "ssd-mobilenet-v2", # 0 the best one???
                "ssd-inception-v2", # 1
                "pednet",           # 2 
                "alexnet",          # 3 
                "facenet",          # 4
                "googlenet"         # 5 also good
                ]

network = network_lst[5]

threshold = 0.5
width = 1080 #1280 # For Logitech 270 #640 # 
height = 608 #960 #480
#camera = '/dev/video0'
camera = '0'
overlay = "box,labels,conf"
print("[INFO] loading model...")
net = jetson.inference.detectNet(network, sys.argv, threshold)

# create the camera and display
camera = jetson.utils.gstCamera(width, height, camera)
# display = jetson.utils.glDisplay() # only if x active

resolution400 = (400,300) # default
resolution800 = (800, 600)
resolution640 = (640, 480)

cur_resolution = (width, height) # resolution800 #640 
scale_factor = cur_resolution[0]/400
resolution_str = str(cur_resolution[0]) +'x' +str(cur_resolution[1])

GREEN_TAG = 0
RED_TAG = 1
interval = 3


def green_light(arg, interval=3):
    global timer
    # print('зашли ', arg)
    if not timer.is_alive() or arg:
        # print('таймер ', timer)
        if arg:
            GPIO.output(GREEN, 1)
            GPIO.output(RED, 0)
        else:
            GPIO.output(GREEN, 0)
            GPIO.output(RED, 1)
        timer = Timer(interval, lambda *a: a)
        timer.start()


def box_square(box):
    (startX, startY, endX, endY) = box.astype("int")
    square = (endX - startX) * (endY - startY)
    return square


# timer for green light delay
timer = Timer(interval, lambda *a: a) 
timer.start()
# off green
green_light(0)


def wdt_func(): # restart system if wdt is not alive
    print ('save before reboot')
    ts = time.asctime( time.localtime(time.time()) )
    with open("/home/a/detector.log", "a") as file:  # append reboot time to the file
        print(ts, sep='\n ', file=file) 
    os.system('sudo reboot')


def put_queue(queue, data):
    # print('put', q_pict.qsize())
    if not queue.qsize() > 3:  # помещать в очередь для web только если в ней не больше 3-х кадров ( статусов )
        # нем смысла совать больше если web не работает и никто не смотрит, или если статус никто не выбирает,
        # ато выжрет всю память однако
        queue.put(data)


def web_is_on():
    """ проверяем работает-ли web путем оценки длины очереди web картинок.
        картинкииз очереди выгребает Flask/
        если никто из этой очереди не get, значит web не работает"""
    return not q_pict.qsize() > 2


def proc():
    global vis, GREEN_TAG, RED_TAG, interval
    # timer to restart detector when main thread crashes
    wdt_tmr = Timer(30, wdt_func) # отключено на время отладки
    wdt_tmr.start()# отключено на время отладки

    if memmon: # mamory allocation monitoring 
        import tracemalloc
        tracemalloc.start()


    while True:

        if memmon:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

        
        wdt_tmr.cancel()# отключено на время отладки
        wdt_tmr = Timer(10, wdt_func)# отключено на время отладки
        wdt_tmr.start()# отключено на время отладки

        frame, width, height = camera.CaptureRGBA(zeroCopy = True)

        detections = net.Detect(frame, width, height, overlay)
        for detection in detections:
            if detection.ClassID ==1: # if pedestrian 
                GREEN_TAG = 1
                print ('detection confidence -', detection.Confidence)

        jetson.utils.cudaDeviceSynchronize()
        # create a numpy ndarray that references the CUDA memory
        # it won't be copied, but uses the same memory underneath
        frame = jetson.utils.cudaToNumpy(frame, width, height, 4)
        #print ("img shape {}".format (aimg1.shape))
        frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGBA2BGR)

        if web_is_on(): # если web работает копируем исходный фрейм для него
            # print('web', q_pict.qsize())
            wframe = frame.copy()
        else:
            pass #wframe = frame
        # print ('frame.shape',frame.shape)

        #frame = cv2.resize(frame, width=400)

        # draw frame resolution
        if net.GetNetworkFPS() != math.inf:
            fps = str(round(net.GetNetworkFPS()))
        else: 
            fps = 'inf...'
        res_string = resolution_str+'  fps-'+ fps + ' net-' + network
        cv2.putText(wframe, res_string, (15, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, 255, 1)
        # draw current time
        # time_str = os.popen("date").read()[:-1]
        # cv2.putText(wframe, time_str, (15, 15), cv2.FONT_HERSHEY_DUPLEX, 0.5, 255, 1)

        # grab the frame dimensions and convert it to a blob from old code
        #(h, w) = frame.shape[:2]

        put_queue(q_pict, wframe)  # put the picture for web in the picture Queue

        # on GREEN if TAG = 1
        green_light(GREEN_TAG)
        put_queue(q_status, GREEN_TAG)
        GREEN_TAG = 0 

        if vis:
            # show the output frame (not actual anymore candidate for del)
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            # if the ESC key was pressed, break from the loop
            if key == 27:
                break
      

        if memmon:
            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)



    green_light(0)
    cv2.destroyAllWindows()
    #vs.stop()
