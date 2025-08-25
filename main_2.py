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

print("cv2.__version__ : ",cv2.__version__)
print("GPIO.VERSION :",GPIO.VERSION)
"""  ###################  SETUP  #################### """

# Video feed setup
#cam = cv2.VideoCapture(0)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()

# Randomizer set up
rand.seed()

# Robot setup
r=Robot('/dev/ttyACM0')
normal_speed = 20
probe_speed = 5
r.set_joint_speed(normal_speed)
r.reset_pos()

# Coordinates setup
pile_max = 2   # number of piles in the setup

xpile1=0
xpile2=0
xpile3=220
xpile4=220
ypile1=-260
ypile2=-380
ypile3=-260
ypile4=-380
zpile=300
apile=180
bpile1=0
bpile2=0
bpile3=35
bpile4=28


xperfodrop=490
xperfopick=490
yperfo=0
zperfodrop=250
zperfopick=125
angle = 10
aperfo=90+angle
bperfo=0

xinser = 200
yinser = 350
zinser = 300
ainser = apile
binser = 0

xtas1 = 0
ytas1 = 300
ztas = 300
atas = apile
btas1 = 0

l_xpile = [xpile1,xpile2] #,xpile3,xpile4]
l_ypile = [ypile1,ypile2] #,ypile3,ypile4]
l_bpile = [bpile1,bpile2] #,bpile3,bpile4]

# Raspberry pins setup --> now defined through the BCM mode
GPIO.setmode(GPIO.BCM)

## definition des pins
Relais = 18
Push_random = 27
Push_single = 17
Push_stop = 23


GPIO.setup(Relais,GPIO.OUT)
GPIO.output(Relais,GPIO.LOW)    ##To make sure the relais starts at low in the program
GPIO.setup(Push_random,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #in PUD_UP to avoid noise in the boolean feedback
GPIO.setup(Push_single,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(Push_stop,GPIO.IN,pull_up_down=GPIO.PUD_UP)  # input to stop the program completely

stop = False

def Push_stop_Handler(pin):
    global stop
    print("Program has been stopped manually")
    stop = True

#GPIO.add_event_detect(Push_stop,GPIO.FALLING,callback = Push_stop_Handler, bouncetime = 1000)

"""  ############  USER CONFIGURATION MODE  ############## """
n_cahier = int(input("Rentrez le nombre de feuilles par cahier: "))
#n_cahier = 2    #number of pages in the book
print("")
print("Choose if random or not")
print("If random, push left, if single pile, push right")
b_random = GPIO.input(Push_random)
b_single = GPIO.input(Push_single)
while (b_random and b_single):
    b_random = GPIO.input(Push_random)
    b_single = GPIO.input(Push_single)

"""  ############  START LOOP SETUP  ########## """
n_max = 10  ## nombre de feuilles maximales autorisées dans la perforatrice
n_perfo = int(n_cahier/n_max) ## nombre de perforations pour un cahier complet
n_reste = n_cahier%n_max ## nombre de feuilles restantes a perforer pour completer le cahier
print("Nombre de perforations de paquets de 10:", n_perfo)
print("Nombre de feuilles restantes:", n_reste)

cam = cv2.VideoCapture(0)
time.sleep(1.5)
ret,frame = cam.read()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)  #detection des marqueurs arucos
corners, ids, rejected = detector.detectMarkers(gray)  #ids is the identifiant of the piles that are empty
if ids is not None:
    b_empty = bool(len(ids)==pile_max)
else:
    b_empty = False
cam.release()

while (b_empty==False):
    """  ########### SART LOADING PERFORATOR  ######### """
    for i_perfo in range(n_perfo+1):
        if i_perfo == n_perfo:
            n_loop = n_reste
        else:
            n_loop = n_max
        if n_loop >0 :
            n_paper = 0
            for n in range(n_loop):
                print("rangeloop ramassage")
                if stop == False:
                    cam = cv2.VideoCapture(0)
                    time.sleep(1)
                    ret,frame = cam.read()
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
                    corners, ids, rejected = detector.detectMarkers(gray)  #ids is the identifiant of the piles that are empty
                    if ids is not None:
                        b_empty = bool(len(ids)==pile_max)
                    else:
                        b_empty = False
                        ids = []
                    cam.release()
                    if  b_empty == False :
                        print("")
                        print("Starting with paper ",n +1 + i_perfo*10)
                        n_paper = n+1     ### to keep sight of the number of papers
                        rand_pile = 0
                        print(ids)
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
                        probe = r.linear_probe([xpile,ypile,40,apile,bpile])

                        if probe==True:
                            print("Starting vacuum")
                            GPIO.output(Relais,GPIO.HIGH)    ### Turn on the vacuun
                            time.sleep(3)
                            
                        print("going up again")
                        r.set_joint_speed(normal_speed)
                        r.linear_move_to_point([xpile,ypile,zpile,apile,bpile])

                        print("going in front of the perforatrice")
                        r.go_to_point([xperfopick-80,yperfo,zperfopick+100,aperfo,bperfo])       
                        r.go_to_point([xperfopick-50,yperfo,zperfopick+50*math.sin(math.radians(angle))*math.sin(math.radians(90-angle))+100,aperfo,bperfo])    
                        r.go_to_point([xperfopick-50,yperfo,zperfopick+50*math.sin(math.radians(angle))*math.sin(math.radians(90-angle)),aperfo,bperfo])  
                        
                        print("probing for perforatrice")
                        r.set_joint_speed(probe_speed)
                        probe = r.linear_probe([xperfopick,yperfo,zperfopick,aperfo,bperfo])     
                        if probe == True :
                            p_perfo = r.get_tool_pose()
                            print("p_perfo: ",p_perfo)
                        else:
                            p_perfo = [xperfopick,yperfo,zperfopick,aperfo,bperfo] 
                        GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuun
                        time.sleep(4)
                        
                        print("going in front of the perforatrice")
                        r.set_joint_speed(normal_speed)
                        r.go_to_point([p_perfo[0]-25,p_perfo[1],p_perfo[2],aperfo,bperfo])
                        r.go_to_point([p_perfo[0]-25,p_perfo[1],p_perfo[2]+100,aperfo,bperfo])    
                        
                    else:
                        print("zero paper left")
                        break
                else :
                    print("Button stop pushed")
                    print("Returning to home position")
                    GPIO.output(Relais,GPIO.LOW) 
                    r.set_joint_speed(normal_speed)
                    r.go_to_foetus_pos()
                    r.reset_pos()
                    print("Process ended")
                    GPIO.cleanup()
                    exit()

            """ ############### START OF PERFORATION ###############"""
            if stop == False and n_paper>0:   
                r.set_joint_speed(probe_speed)
                print("\npushing the papers to the side\n")
                r.linear_move_to_point([p_perfo[0]-33,p_perfo[1]-200,p_perfo[2]+100,aperfo,bperfo])
                r.linear_move_to_point([p_perfo[0]-30,p_perfo[1]-200,p_perfo[2]-5,aperfo,bperfo])   
                r.linear_move_to_point([p_perfo[0]-30,p_perfo[1]-130,p_perfo[2]-5,aperfo,bperfo])
                #r.linear_move_to_point([p_perfo[0]-10,p_perfo[1],p_perfo[2],aperfo,bperfo])
                #r.linear_move_to_point([p_perfo[0]-10,p_perfo[1]+30,p_perfo[2],aperfo,bperfo])
                r.linear_move_to_point([p_perfo[0]-35,p_perfo[1]-110,p_perfo[2],aperfo,bperfo])
                r.linear_move_to_point([p_perfo[0]-35,p_perfo[1]-110,p_perfo[2]+100,aperfo,bperfo])
            else:
                print("Returning to home position")
                GPIO.output(Relais,GPIO.LOW) 
                r.set_joint_speed(normal_speed)
                r.go_to_foetus_pos()
                r.reset_pos()
                print("Process ended")
                GPIO.cleanup()
                exit()
            #### PUT HERE THE ACTIVATION OF THE PERFORATRICE

            """ ############### START UNLOADING PERFORATOR ############"""
            for n in range(n_paper):
                if stop == False:
                    print("Starting unloading paper ",n +1 + i_perfo*10)
                    
                    print("going in front of the perforatrice")
                    r.set_joint_speed(normal_speed)
                    r.go_to_point([xperfopick-80,yperfo,zperfopick+100,aperfo,bperfo])
                    r.go_to_point([xperfopick-50,yperfo,zperfopick+50*math.sin(math.radians(angle))*math.sin(math.radians(90-angle))+100,aperfo,bperfo])
                    r.go_to_point([xperfopick-50,yperfo,zperfopick+50*math.sin(math.radians(angle))*math.sin(math.radians(90-angle)),aperfo,bperfo])
                    
                    print("probing for the perfo")
                    r.set_joint_speed(probe_speed)
                    print("xperfopick: ",xperfopick)
                    print("zperfopick: ",zperfopick)
                    probe = r.linear_probe([xperfopick,yperfo,zperfopick,aperfo,bperfo])
                    if probe==True:
                        print("Starting vacuum")
                        GPIO.output(Relais,GPIO.HIGH)    ### Turn on the vacuum
                        time.sleep(3)
                        
                    print("taking out the paper from the slot")
                    p_perfo = r.get_tool_pose()
                    r.linear_move_to_point([p_perfo[0]-20,p_perfo[1],p_perfo[2],p_perfo[3],p_perfo[4]])
                    r.linear_move_to_point([p_perfo[0]-20,p_perfo[1],p_perfo[2]+150,p_perfo[3],p_perfo[4]])
                    time.sleep(1)
                    
                    print("going in front of the perforatrice")
                    r.set_joint_speed(normal_speed)
                    r.go_to_point([xperfopick-200,yperfo,zperfopick+150,aperfo,bperfo])
                    
                    print("going above a 'tas'")
                    r.go_to_point([xtas1,ytas1,ztas,atas,btas1])
                    
                    print("going down until contact")
                    r.set_joint_speed(probe_speed)
                    probe = r.linear_probe([xtas1,ytas1,20,atas,btas1])            
                    GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuum
                    time.sleep(4)
                    
                    print("going above a 'tas'\n")
                    r.linear_move_to_point([xtas1,ytas1,ztas,atas,btas1])
                else:
                    print("Returning to home position")
                    GPIO.output(Relais,GPIO.LOW) 
                    r.set_joint_speed(normal_speed)
                    r.go_to_foetus_pos()
                    r.reset_pos()
                    print("Process ended")
                    GPIO.cleanup()
                    exit()

            """ ############### START RECALIBRATION  ##########"""
            print("returning to home position")
            r.set_joint_speed(normal_speed)
            r.go_to_foetus_pos()
            r.reset_pos()
            
    """ ########### START ADDING SEPARATOR  ############"""
    print("\ngoing above separator pile")
    r.go_to_point([xinser,yinser,zinser,ainser,binser])
    
    r.set_joint_speed(probe_speed)
    print("probing for the separator pile")
    probe = r.linear_probe([xinser,yinser,20,ainser,binser])
    if probe == True:
        print("Starting vacuum")
        GPIO.output(Relais,GPIO.HIGH)    ### Turn on the vacuum
        time.sleep(3)
        
    r.set_joint_speed(normal_speed)
    print("going above separator pile")
    r.linear_move_to_point([xinser,yinser,zinser,ainser,binser])
    
    print("going above a 'tas'")
    r.go_to_point([xtas1,ytas1,ztas,atas,btas1])
    
    print("going down until contact")
    r.set_joint_speed(probe_speed)
    probe = r.linear_probe([xtas1,ytas1,20,atas,btas1])            
    GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuum
    time.sleep(3)
    
    print("going above a 'tas'")
    r.linear_move_to_point([xtas1,ytas1,ztas,atas,btas1])
    
    print("returning to home position")
    print("Cahier is finished \n")
    r.set_joint_speed(normal_speed)
    r.go_to_foetus_pos()
    r.reset_pos()
    
""" ######### RETURN TO INITIAL CONFIGURATION  #######"""
print("returning to home position")
r.set_joint_speed(normal_speed)
r.go_to_foetus_pos()
r.reset_pos()
GPIO.cleanup()