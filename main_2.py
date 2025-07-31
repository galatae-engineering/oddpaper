import sys
import RPi.GPIO as GPIO
import cv2
import numpy as np
import os
import math
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
normal_speed = 80
probe_speed = 15
r.set_joint_speed(normal_speed)
r.reset_pos()

# Coordinates setup
pile_max = 4   # number of piles in the setup

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


xperfo=350
yperfo=0
zperfo=150
aperfo=110
bperfo=0

xtas1 = 200
ytas1 = 350
ztas = 300
atas = apile
btas = 0

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
n_cahier = 50    #number of pages in the book
print("")
print("Choose if random or not")
print("If random, push left, if single pile, push right")
b_random = GPIO.input(Push_random)
b_single = GPIO.input(Push_single)
while (b_random and b_single):
    b_random = GPIO.input(Push_random)
    b_single = GPIO.input(Push_single)
"""  ############  USER CONFIGURATION END   ############## """
"""  ############  START LOOP SETUP  ########## """
n_max = 10  ## nombre de feuilles maximales autorisées dans la perforatrice
n_perfo = int(n_cahier/n_max) ## nombre de perforations pour un cahier complet
n_reste = n_cahier%n_max ## nombre de feuilles restantes a perforer pour completer le cahier
print("Nombre de perforations de paquets de 10:", n_perfo)
print("Nombre de feuilles restantes:", n_reste)
"""  ############  END LOOP SETUP  ########### """
"""  ########### SART LOADING PERFO  ######### """
for i_perfo in range(n_perfo+1):
    if i_perfo == n_perfo:
        n_loop = n_reste
    else:
        n_loop = n_max
    if n_loop >0 :
        for n in range(n_loop):
            cam = cv2.VideoCapture(0)
            time.sleep(0.5)
            ret,frame = cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #detection d un marquer aruco appartenant a la bibliotheque definie
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
            #recuperation du data de l aruco detecte
            corners, ids, rejected = detector.detectMarkers(gray)  #ids is the identifiant of the piles that are empty

            if ids is not None:   
                cv2.aruco.drawDetectedMarkers(frame,corners,ids)
            else:
                ids = []
            
            cam.release()
            if  len(ids)<pile_max :
                b_empty = False
                print("")
                print("Starting with paper ",n +1 + i_perfo*10)
                rand_pile = 0
                if not b_random :
                    print("Random mode chosen")
                    rand_pile = rand.randint(0,pile_max-1)
                    while [rand_pile] in ids :
                        rand_pile = rand.randint(0,pile_max-1)
                elif not b_single :
                    print("Normal mode chosen")
                    while [rand_pile] in ids :
                        rand_pile +=1
                print("will go to pile",rand_pile+1)
                xpile = l_xpile[rand_pile]
                ypile = l_ypile[rand_pile]
                bpile = l_bpile[rand_pile]

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
                if probe == True :
                    p_perfo = r.get_tool_pose()
                    print("p_perfo: ",p_perfo)
                else:
                    p_perfo = [xperfo,yperfo,zperfo,aperfo,bperfo]
                GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuun
                time.sleep(5)
                
                print("going in front of the perforatrice")
                r.set_joint_speed(normal_speed)
                r.go_to_point([xperfo-200,yperfo,zperfo,aperfo,bperfo])        
            else:
                print("zero paper left")
                b_empty = True
                break
        """ ############### END LOADING PERFO ############### """
        """ ############### START OF PERFO ###############"""
        time.sleep(0.5)
        r.set_joint_speed(probe_speed)
        print("pushing the papers to the side")
        r.go_to_point([p_perfo[0]-27,p_perfo[1]-150,p_perfo[2],p_perfo[3],p_perfo[4]])
        r.go_to_point([p_perfo[0]-27,p_perfo[1]-100,p_perfo[2],p_perfo[3],p_perfo[4]])
        r.go_to_point([p_perfo[0]-10,p_perfo[1],p_perfo[2],p_perfo[3],p_perfo[4]])

        #### PUT HERE THE ACTIVATION OF THE PERFORATRICE
        """ ############### END OF PERFO ##############"""
        """ ############### SART UNLOADING ############"""
        if n_loop>0:
            for n in range(n_loop):
                print("Starting unloadobg paper ",n +1 + i_perfo*10)
                
                print("going in front of the perforatrice")
                r.set_joint_speed(normal_speed)
                r.go_to_point([xperfo-200,yperfo,zperfo,aperfo,bperfo])
                time.sleep(0.5)
                
                print("probing for the perfo")
                r.set_joint_speed(probe_speed)
                probe = r.probe([xperfo,yperfo,zperfo,aperfo,bperfo])
                if probe==True:
                    print("Starting vacuum")
                    GPIO.output(Relais,GPIO.HIGH)    ### Turn on the vacuum
                    time.sleep(5)
                    
                print("taking out the paper from the slot")
                p_perfo = r.get_tool_pose()
                r.go_to_point([p_perfo[0]-10,p_perfo[1],p_perfo[2],p_perfo[3],p_perfo[4]])
                r.go_to_point([p_perfo[0]-10+math.sin(math.radians(10))*100,p_perfo[1],p_perfo[2]+math.cos(math.radians(10))*100,p_perfo[3],p_perfo[4]])
                time.sleep(1)
                
                print("going in front of the perforatrice")
                r.set_joint_speed(normal_speed)
                r.go_to_point([xperfo-200,yperfo,zperfo,aperfo,bperfo])
                
                print("going above a 'tas'")
                r.go_to_point([xtas1,ytas1,ztas,atas,btas])
                
                print("going down until contact")
                r.set_joint_speed(probe_speed)
                probe = r.probe([xtas1,ytas1,-30,atas,btas])            
                GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuum
                time.sleep(5)
                
                print("going above a 'tas'")
                r.go_to_point([xtas1,ytas1,ztas,atas,btas])
            
        """ ############### END UNLOADING  ############"""
        print("returning to home position")
        r.set_joint_speed(normal_speed)
        r.go_to_foetus_pos()
        r.set_joint_speed(normal_speed)
        r.reset_pos()

