import cv2

import numpy as np

import os

cam = cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    cv2.imshow('Camera',frame)
    
    if cv2.waitkey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()