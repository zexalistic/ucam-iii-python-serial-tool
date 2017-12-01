# coding:utf-8
import ucam
import time
import sys

cam = ucam.UCam()

# cam.reset()
# print("send reset")
# time.sleep(5)

synced = cam.sync()
print("synced is ready? {}".format(synced))

if synced:
    # after synced, have to wait 1 to 2 seconds
    time.sleep(2)
    filename = 'test.jpg'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    cam.take_picture(filename)
