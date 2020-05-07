''' 30 ms per frame. too slow'''
from jetcam.csi_camera import CSICamera
import cv2, time

camera = CSICamera(width=1080, height=720, capture_width=1080, capture_height=720, capture_fps=30)

while True: # 30 ms per frame in circle - too much..
    ts = time.time()
    frame = camera.read()
    
    
    time_str = f'{(time.time()-ts)*1000:.4} msec/frm'
    # print(time_str)
    cv2.putText(frame, time_str, (15, 15), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255,255,255), 1)
    cv2.imshow('frm', frame)
    k = cv2.waitKey(1)
    if k==27:
        break
cv2.destroyAllWindows()
