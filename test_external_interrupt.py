import RPi.GPIO as GPIO
import time
import atexit
import sys

GPIO.cleanup()
# Raspberry pins setup --> now defined through the BCM mode
GPIO.setmode(GPIO.BCM)

pin_stop = 23
pin_led = 22
GPIO.setup(pin_stop,GPIO.IN,pull_up_down=GPIO.PUD_UP)
#GPIO.setmode(pin_led,GPIO.OUT)
#GPIO.OUTPUT(pin_led,GPIO.LOW)
def button_stop(pin):
    global ex
    print("La led va s'allumer")
    print("hellooo")
    ex = True
    
def exit_handler():
    print("Program has ended")
atexit.register(exit_handler)
GPIO.add_event_detect(pin_stop,edge = GPIO.FALLING,callback = button_stop, bouncetime = 1000)
ex = False
while True:
    time.sleep(0.2)
    print(ex)
    if ex == True:
        GPIO.cleanup()
        exit()
    #GPIO.OUTPUT(pin_led,GPIO.LOW)
