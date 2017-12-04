# coding:utf-8

import serial, commands
import time
import re
from binascii import hexlify, unhexlify
from struct import pack, unpack
import math
import codecs

class UCam(object):
    """
    an interface to communicate with a uCam-II camera
    over a UART serial connection.
    """

    def __init__(self):
        # change serial device name to yours 
        self.ser = serial.Serial('/dev/tty.usbserial-xxxxxxxxx', baudrate=921600, timeout=.01)
        self.synced = False
        print("initialized!")

    def sync(self):
        num_tries = 60      # 60 times is enough by the documents
        while num_tries > 0:
            if self._sync():
                return True
            num_tries -= 1
        return False

    def _write(self, string):

        
        return self.ser.write(bytearray(unhexlify(string)))

    
    def _matches(self, pattern, packet):
        packet_str = hexlify(packet)
        return re.match(pattern, packet_str.decode()) is not None

    def _sync(self):
        time.sleep(.05)
        self._write(commands.sync())
        read = self.ser.read(6)
        print(read)
        if self._matches(commands.ack('0d', '..'), read):
            if self._matches(commands.sync(), self.ser.read(6)):
                self._write(commands.ack('0d', '00'))
                return True
        return False

    def _initial(self):
        init_cmd = commands.initial('07', '07', '07')
        print("init cmd {}".format(init_cmd))




        self._write(init_cmd)
        # print("send init commandだよ")
        # print(init_cmd)
        # self.ser.write(bytearray(unhexlify('aa0100070707')))

        read = self._wait_for_bytes(6)

        print("return ack, maybe AA 0E 01 xx 00 00")
        print('ack {}'.format(read))


        assert self._matches(commands.ack('01', '..'), read)

    def _wait_for_bytes(self, i):
        bytearr = bytearray(i)
        cur = 0
        while cur < i:
            read = self.ser.read(1)
            if len(read) == 1:
                bytearr[cur] = read[0]
                cur += 1
        return bytearr

    def _set_pkg_size(self):
        # set package size 512 bytes
        self._write(commands.set_pkg_size('00', '02'))
        assert self._matches(commands.ack('06', '..'), self._wait_for_bytes(6))

    def _snapshot(self):
        self._write(commands.snapshot('00', '00', '00'))
        assert self._matches(commands.ack('05', '..'), self._wait_for_bytes(6))

    def _get_picture(self):
        """
        sends the GET PICTURE command and receives the corresponding DATA command.
        Returns the number of packets to be read.
        """
        self._write(commands.get_picture('01'))
        assert self._matches(commands.ack('04', '..'), self._wait_for_bytes(6))
        # receive DATA
        data = self._wait_for_bytes(6)
        print("data is ", data)
        assert self._matches(commands.data('01', '..', '..', '..'), data)

        print("hexlify(data) is: ", hexlify(data))

        print("data is", data)
        print("data[-3:] is ", data[-3:])

        # below line is too redundant... to avoid "UnicodeDecodeError: 'utf-8' codec can't decode byte 0x9a in position 0: invalid start byte"
        # img_size = unpack('<I', (codecs.decode(codecs.encode(unhexlify(hexlify(data[-3:])), 'hex'), 'hex') + b'\x00'))[0]
        # img_size = unpack('<I', (unhexlify(hexlify(data[-3:])) + b'\x00'))[0]

        # this is simple, maybe best
        img_size = unpack('<I', (data[-3:] + b'\x00'))[0]


        print("image size is {}".format(img_size))

        ### num_pkgs must be int
        # num_pkgs = img_size / (512 - 6)
        num_pkgs = math.floor(img_size / (512 - 6))


        print("num packages: {}".format(num_pkgs))

        self._write(commands.ack('00', '00'))
        return img_size

    def _write_picture(self, img_size, name='pic.jpeg'):

        ### num_pkgs must be int
        # num_pkgs = img_size / (512 - 6)
        num_pkgs = math.floor(img_size / (512 - 6))


        with open(name, 'wb+') as f:
            for i in range(1, num_pkgs + 1):
                # print("getting package {}".format(i))
                read = self._wait_for_bytes(512)
                # print(read)
                f.write(read[4:-2])

                ### hex_idx must be str
                # hex_idx = hexlify(pack('H', i))
                hex_idx = hexlify(pack('H', i)).decode()

                # print("hex_idx is {}".format(hex_idx))
                self._write(commands.ack('00', '00', hex_idx[:2], hex_idx[-2:]))
            f.write(self._wait_for_bytes(img_size - num_pkgs * (512 - 6) + 2))
            f.close()
        # ACK end of data transfer
        self._write(commands.ack('f0', 'f0'))
        print("taken picture, finish!")

    def take_picture(self, name='pic.jpeg'):
        # initialize for JPEG, VGA
        self._initial()
        
        # set package size to 512 bytes
        self._set_pkg_size()

        # compresed snapshot pic
        self._snapshot()

        # get picture (snapshot)
        num_pkgs = self._get_picture()

        # receive img data pkgs
        self._write_picture(num_pkgs, name)

    def reset(self):
        self._write(commands.reset())

