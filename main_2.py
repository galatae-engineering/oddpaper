import sys
import RPi.GPIO as GPIO
import time
import random as rand
sys.path.append('../galatae-api/')
from robot import Robot


"""  ###################  SETUP   #################### """

rand.seed()

r=Robot('/dev/ttyACM0')
normal_speed = 20
probe_speed = 7
r.set_joint_speed(normal_speed)
r.reset_pos()

xpile13=150    ##Coordonnées des piles de feuilles en entrée avec x,y,a,b qui varient
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
zperfo=100
aperfo=110
bperfo=0

l_xpile = [xpile13,xpile24,xpile13,xpile24]
l_ypile = [ypile12,ypile12,ypile34,ypile34]
l_bpile = [bpile1,bpile2,bpile3,bpile4]

GPIO.setmode(GPIO.BCM)

## definition des pins
Relais = 18
Push_random = 4
Push_single = 17

GPIO.setup(Relais,GPIO.OUT)
GPIO.output(Relais,GPIO.LOW)    ##To make sure the relais starts at low in the program
GPIO.setup(Push_random,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(Push_single,GPIO.IN,pull_up_down=GPIO.PUD_UP)

"""  ###################  END SETUP   #################### """
"""  ############  USER CONFIGURATION MODE  ############## """
n_cahier = 54
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
n_perfo = n_cahier/n_max ## nombre de perforations pour un cahier complet
n_reste = n_cahier%n_max ## nombre de feuilles restantes a perforer pour completer le cahier
print("Nombre de perforations de paquets de 10:", n_perfo)
print("Nombre de feuilles restantes:", n_reste)

for n in range(n_max):
    print("")
    print("Starting with paper n:",n)
    if not b_random :
        print("Random mode chosen")
        rand_pile = rand.randint(0,3)
    elif not b_single :
        print("Normal mode chosen")
        rand_pile = 0
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
    
    
print("returning to home position")
r.go_to_foetus_pos()