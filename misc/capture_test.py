""" gets detections from some detector. Build treks based on iou algorythm.
    gets frames, make iou's to each in the frames in detection set. 
    Assign frame to the end of the track. Kalman filtering implemented.
"""
import time
import cv2
import numpy as np

video_src = "/home/a/dt3_jetson/U524806_3.avi"

def proc():
    cap = cv2.VideoCapture(video_src)
    while True:
        tss= time.time()
        ret, img = cap.read()
        frame_rate_str = f'{(time.time()-tss)*1000:.3} msec/frm'
        cv2.putText(img, frame_rate_str, (15, 45), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255,255,255), 1)
        
        cv2.imshow("Frame", img)
        key = cv2.waitKey(1) & 0xFF
        # if the `ESC` key was pressed, break from the loop
        if key == 27:
            break

        # if memmon:
        #     print("[ Top 10 ]")
        #     for stat in top_stats[:10]:
        #         print(stat)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    proc()
