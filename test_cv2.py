import cv2

import numpy as np

import os


cam = cv2.VideoCapture(0)

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()

while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #detection d un marquer aruco appartenant a la bibliotheque definie
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    
    #recuperation du data de l aruco detecte
    corners, ids, rejected = detector.detectMarkers(gray)
    
    print("Detected markers:", ids)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame,corners,ids)
    cv2.imshow('Camera',frame)
    
    if cv2.waitKey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()