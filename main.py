import sys
#import RPi.GPIO as GPIO
import time
sys.path.append('../galatae-api/')
from robot import Robot


"""  ###################  SETUP   #################### """

r=Robot('/dev/ttyACM0')
r.set_joint_speed(10)
r.reset_pos()

x=420
y=0
z0=150
yperfo=150
z=z0

pPerfo = [0,250,z0+100,0,0]
          
#GPIO.setmode(GPIO.BCM)

## definition des pins
Sensor = 17
Relais = 18
Step = False
bSensor = False #True

#GPIO.setup(Sensor,GPIO.IN,pull_up_down=GPIO.PUD_UP)
#GPIO.setup(Relais,GPIO.OUT)

"""  ###################  END SETUP   #################### """

print(r.get_tool_pose())
r.go_to_point([x,y,z0,180,0])

#bSensor = GPIO.input(Sensor)
while bSensor == False:      #### Wait untils it detects something with the sensor
    z=z-0.1
    if z<=0:
        bSensor = True
        print("z is",z)
    else:
        point=[x,y,z,180,0]
        #print(point)
        r.go_to_point(point)
        #print(r.get_tool_pose())
        #bSensor = GPIO.input(Sensor)

        
#GPIO.output(Relais,GPIO.HIGH)   ### Activate the vacuum
print("Vaccum is activated")
time.sleep(5)
print("going up high again")
z=z0+100
r.go_to_point([x,y,z,180,0])

y=yperfo
x=0
r.go_to_point([x,y,z,110,0])
print("starting progression towards the perforatrice... waiting for sensor input...")
#bSensor = GPIO.input(Sensor)
while bSensor == False:      #### Wait untils it detects something with the sensor
    y=y+0.1
    if y>=300:
        bSensor = True
        print("y is",y)
    else:
        point=[x,y,z,110,0]
        #print(point)
        r.go_to_point(point)
        #print(r.get_tool_pose())
        #bSensor = GPIO.input(Sensor)

#GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuun
print("Vacuun is desactivated")
time.sleep(5)
print("returning to home position")
r.go_to_foetus_pos()

"""
while True:
    if (GPIO.input(Sensor) == False and Step == False) :
        GPIO.output(Relais,GPIO.HIGH)
        Step = True
        print("activating the relais...")
        time.sleep(5)
    elif (GPIO.input(Sensor) == False and Step == True) : 
        GPIO.output(Relais,GPIO.LOW)
        print("relais being put to sleep...")
        Step= False
        time.sleep(5)
"""
"""
Structure du code général:
import robot
import gpio

set velocity at V
set x,y of pile
set zMax : hauteur de sécurité dy robot, garantie touours bien au dessus de la pile
"""
    
""" ALERTE ROUGES PROBLEMES DE BUGS RENCONTRES"""
""" 1| le programme n'est pas bloque par le mouvement du robot, les time.sleep commencent donc des l'envoi de la commande
Solution possible : programmer un while avec comparaison des coordonnees afin de bloquer le programme.
Demander a roger de l'implementer dans le programme core du robot
ajouter de petits (qques ms) a chaque deplace,ent dans le loop descente"""
