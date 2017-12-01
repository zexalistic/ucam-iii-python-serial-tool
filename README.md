# uCam-II-Python

This is for using uCam-II(4D Systems) and take jpeg picture by Python3

I wrote this by using [nichhk/ucam-pyserial](https://github.com/nichhk/ucam-pyserial) as a reference.


[4D Systems | uCAM-II](https://www.4dsystems.com.au/product/uCAM_II/)


I use FTDI USB-serial exchange board to communicate with uCam-II

in japan, we can get at switchscience 

[FTDI USBシリアル変換アダプター Rev.2 - スイッチサイエンス](https://www.switch-science.com/catalog/2782/)


### Using


You have to use `pyserial`, `binascii`, `struct` packages.

Install those if you don't installed yet before running script.


And you have to write serial device name in `ucam.py` code. 
(I use MacOS so wrote '/dev/tty.usbserial-xxxxxxx' as initial)


And run script, `$ python main.py`.
After run the script, test.jpg is outputted if taking picture succeeded.