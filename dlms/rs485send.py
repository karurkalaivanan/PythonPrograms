import subprocess
import serial
import time

command = 'echo 410 > /sys/class/gpio/export'
subprocess.run(command,shell=True,check=True)

command = 'echo out > /sys/class/gpio/P6_2/direction'
subprocess.run(command,shell=True,check=True)

command = 'echo 1 > /sys/class/gpio/P6_2/value'
subprocess.run(command,shell=True,check=True)

# ser = serial.Serial('/dev/ttySC4',baudrate=9600,timeout=1)
ser = serial.Serial('COM6',baudrate=9600,timeout=1)
data = bytes([0x01,0x03,0x0F,0x58,0x00,0x02,0x46,0xCC])
ser.write(data)

command = 'echo 0 > /sys/class/gpio/P6_2/value'
subprocess.run(command,shell=True,check=True)

try:
 while True:
  if ser.in_waiting > 0:
   received_data = ser.read(ser.in_waiting)
   print("Received data:",received_data.hex())
   break
  else:
   print("No Data available")
  time.sleep(0.5)
except KeyboardInterrupt:
 print("Stopped by user.")
finally:
 ser.close()