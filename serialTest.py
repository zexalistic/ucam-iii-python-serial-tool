import serial

ser = serial.Serial('/dev/tty.usbserial-AI03CNY6', timeout=.01)
hello_str = bytearray('deadbeef'.encode())

read = ser.read(1)

print(hello_str)
print(hello_str.decode())

ser.close()
