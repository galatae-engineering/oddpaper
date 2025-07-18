import sys
import RPi.GPIO as GPIO
import cv2
import numpy as np
import os
import time
import random as rand
sys.path.append('../galatae-api/')
from robot import Robot


"""  ###################  SETUP   #################### """

# Video feed setup
#cam = cv2.VideoCapture(0)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()

# Randomizer set up
rand.seed()

# Robot setup
r=Robot('/dev/ttyACM0')
normal_speed = 20
probe_speed = 7
r.set_joint_speed(normal_speed)
r.reset_pos()

# Coordinates setup
pile_max = 4

xpile13=150    
xpile24=0
ypile12=-400
ypile34=-250
zpile=300
apile=180
bpile1=0
bpile2=0
bpile3=0
bpile4=0


xperfo=400
yperfo=0
zperfo=150
aperfo=110
bperfo=0

l_xpile = [xpile13,xpile24,xpile13,xpile24]
l_ypile = [ypile12,ypile12,ypile34,ypile34]
l_bpile = [bpile1,bpile2,bpile3,bpile4]

# Raspberry pins setup --> now defined through the BCM mode
GPIO.setmode(GPIO.BCM)

## definition des pins
Relais = 18
Push_random = 27
Push_single = 17

GPIO.setup(Relais,GPIO.OUT)
GPIO.output(Relais,GPIO.LOW)    ##To make sure the relais starts at low in the program
GPIO.setup(Push_random,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #in PUD_UP to avoid noise in the boolean feedback
GPIO.setup(Push_single,GPIO.IN,pull_up_down=GPIO.PUD_UP)

"""  ###################  END SETUP   #################### """
"""  ############  USER CONFIGURATION MODE  ############## """
n_cahier = 14    #number of pages in the book
print("")
print("Choose if random or not")
print("If random, push left, if single pile, push right")
b_random = GPIO.input(Push_random)
b_single = GPIO.input(Push_single)
while (b_random and b_single):
    b_random = GPIO.input(Push_random)
    b_single = GPIO.input(Push_single)
"""  ############  USER CONFIGURATION END   ############## """

n_max = 10  ## nombre de feuilles maximales autorisées dans la perforatrice
n_perfo = int(n_cahier/n_max) ## nombre de perforations pour un cahier complet
n_reste = n_cahier%n_max ## nombre de feuilles restantes a perforer pour completer le cahier
print("Nombre de perforations de paquets de 10:", n_perfo)
print("Nombre de feuilles restantes:", n_reste)
for i_perfo in range(n_perfo+1):
    if i_perfo == n_perfo:
        n_loop = n_reste
    else:
        n_loop = n_max
    if n_loop >0 :
        for n in range(n_loop):
            cam = cv2.VideoCapture(0)
            time.sleep(0.5)
            """ Checking the wheter the piles are empty"""
            ret,frame = cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #detection d un marquer aruco appartenant a la bibliotheque definie
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
            #recuperation du data de l aruco detecte
            corners, ids, rejected = detector.detectMarkers(gray)
            print("arucos detected: ",ids)   #ids is the identifiant of the piles that are empty

            if ids is not None:   
                cv2.aruco.drawDetectedMarkers(frame,corners,ids)
            cv2.imshow('Camera',frame)
            
            cam.release()
            cv2.destroyAllWindows()
            
            """ Start feeding the perforatrice process"""
            if  len(ids)<pile_max :
                print("")
                print("Starting with paper n:",n + i_perfo*10)
                print("brandom: ",b_random)
                print("bnormal: ",b_single)
                rand_pile = 0
                if not b_random :
                    print("Random mode chosen")
                    rand_pile = rand.randint(0,pile_max-1)
                    print("Pile selected : ",rand_pile)
                    while [rand_pile] in ids :
                        rand_pile = rand.randint(0,pile_max-1)
                        print("Pile selected : ",rand_pile)
                elif not b_single :
                    print("Normal mode chosen")
                    while [rand_pile] in ids :
                        rand_pile +=1
                        print("Pile selected : ",rand_pile)
                print("will go to pile",rand_pile+1)
                xpile = l_xpile[rand_pile]
                ypile = l_ypile[rand_pile]
                bpile = l_bpile[rand_pile]

                print("x coordinate:",xpile,"; y coordinate:",ypile,"; b coordinate:",bpile)

                print("Going above the pile")
                r.go_to_point([xpile,ypile,zpile,apile,bpile])


                print("Descending until contact")
                r.set_joint_speed(probe_speed)
                probe = r.probe([xpile,ypile,-30,apile,bpile])

                if probe==True:
                    print("Starting vacuum")
                    GPIO.output(Relais,GPIO.HIGH)    ### Turn on the vacuun
                    time.sleep(5)
                    
                print("going up again")
                r.set_joint_speed(normal_speed)
                r.go_to_point([xpile,ypile,zpile,apile,bpile])

                print("going in front of the perforatrice")
                r.go_to_point([xperfo-200,yperfo,zperfo,aperfo,bperfo])

                print("probing for perforatrice")
                r.set_joint_speed(probe_speed)
                probe = r.probe([xperfo,yperfo,zperfo,aperfo,bperfo])

                GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuun
                time.sleep(3)
                
                print("going in front of the perforatrice")
                r.set_joint_speed(normal_speed)
                r.go_to_point([xperfo-200,yperfo,zperfo,aperfo,bperfo])        
            else:
                print("zero paper left")
                break
        print("returning to home position")
        r.go_to_foetus_pos()
        r.set_joint_speed(normal_speed)
        r.reset_pos()

