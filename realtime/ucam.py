import serial, commands
import time
import re
from binascii import hexlify, unhexlify
from struct import pack, unpack
import codecs
import io
import numpy as np
import cv2

class UCam(object):
    """
    an interface to communicate with a uCam-II camera
    over a UART serial connection.
    """
    def __init__(self):
        # change serial device name to yours 
        self.ser = serial.Serial('/dev/ttyUSB0', baudrate=921600, timeout=.1)
        self.synced = False
        print("Serial port set")

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
        if self._matches(commands.ack('0d', '..'), read):
            if self._matches(commands.sync(), self.ser.read(6)):
                self._write(commands.ack('0d', '00'))
                return True
        return False

    def _initial(self):
        init_cmd = commands.initial('03', '01', '03')

        self._write(init_cmd)

        read = self._wait_for_bytes(6)

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

    def _set_baudrate(self, first_divider, second_divider):
        self._write(commands.set_baudrate('01','00'))
        assert self._matches(commands.ack('07', '..'), self._wait_for_bytes(6))
        

    def _get_picture(self):
        """
        sends the GET PICTURE command and receives the corresponding DATA command.
        Returns the number of packets to be read.
        """
        self._write(commands.get_picture('02'))
        assert self._matches(commands.ack('04', '..'), self._wait_for_bytes(6))
        # receive DATA
        data = self._wait_for_bytes(6)
        assert self._matches(commands.data('02', '..', '..', '..'), data)
        img_size = unpack('<I', (data[-3:] + b'\x00'))[0]
        self._write(commands.ack('00', '00'))

        return img_size

    def _write_picture(self, name):
        read = self._wait_for_bytes(4800)
        gray = np.array(read).reshape(60,80)
        cv2.imshow('image',gray)
        cv2.waitKey(1)
        # ACK end of data transfer
        self._write(commands.ack('0A', '00','01','00'))

    def take_picture(self, name):
        # get picture 
        self._get_picture()

        # receive img data pkgs
        self._write_picture(name)

    def reset(self):
        self._write(commands.reset())

