# coding:utf-8
import ucam
import time
import sys
import os

cam = ucam.UCam()

synced = cam.sync()
print("synced is ready? {}".format(synced))

if synced:
    if len(sys.argv) == 1:
        dir_name = 'test'
    else:
        dir_name = sys.argv[1]
    os.mkdir(dir_name)
    path = os.getcwd()+ '/' + dir_name
    os.chdir(path)

    cam._initial()
    for i in range(10):
        name = 'image_' + str(i) + '.png'
        cam.take_picture(name)
