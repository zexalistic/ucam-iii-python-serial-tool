import ucam
import time
import sys
import os

cam = ucam.UCam()
synced = cam.sync()
print("synced is ready? {}".format(synced))

if synced:
    cam._initial()
    time.sleep(.2)
    while(1):
        name = 'test.jpg'
        cam.take_picture(name)
