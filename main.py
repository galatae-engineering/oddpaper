import sys
import time
sys.path.append('../galatae-api/')
from robot import Robot

r=Robot('/dev/ttyACM0')

r.reset_pos()
r.set_joint_speed(10)
r.go_to_point([420,0,150,180,0])
time.sleep(1)
r.go_to_point([420,0,150,180,0])
time.sleep(5)
r.go_to_point([420,0,-20,180,0])
r.set_joint_speed(5)
r.go_to_point([420,0,-95,180,0])
time.sleep(10)
r.set_joint_speed(10)
r.go_to_foetus_pos()