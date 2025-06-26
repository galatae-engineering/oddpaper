import sys
import RPi.GPIO as GPIO
import time
sys.path.append('../galatae-api/')
from robot import Robot


"""  ###################  SETUP   #################### """

r=Robot('/dev/ttyACM0')
r.set_joint_speed(7)
r.reset_pos()

x=420
y=0
z=150

GPIO.setmode(GPIO.BCM)

## definition des pins
Sensor = 17
Relais = 18
Step = False
bSensor = False

GPIO.setup(Sensor,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(Relais,GPIO.OUT)

"""  ###################  END SETUP   #################### """


r.go_to_point([x,y,z,180,0])
time.sleep(5)
bSensor = GPIO.input(Sensor)
while bSensor == True:      #### Wait untils it detects something with the sensor
    z=z-5
    if z<=0:
        bSensor = False
    else:
        r.go_to_point([x,y,z,180,0])
        print(r.get_pose())
        bSensor = GPIO.input(Sensor)
        
GPIO.output(Relais,GPIO.HIGH)   ### Activate the vacuum
print("Vaccum is activated")
time.sleep(5)
print("returning to home position")
r.go_to_foetus_pos()
bSensor = GPIO.input(Sensor)
while bSensor == True:      #### Wait untils it detects something with the sensor
    bSensor = GPIO.input(Sensor)
GPIO.output(Relais,GPIO.LOW)    ### Turn off the vacuun
print("Vacuun is desactivated")
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
    
    
