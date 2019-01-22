# coding:utf-8
import ucam
import time
import sys

cam = ucam.UCam()

synced = cam.sync()
print("synced is ready? {}".format(synced))

if synced:
    cam.take_picture('test.png')
