from gpiozero import CPUTemperature
import time
import socket
cpu = CPUTemperature()
temp = cpu.temperature
time_epoch = int(time.time())
tuple_uart = str(time_epoch) + ":" + str(temp)
print tuple_uart

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host ="localhost"
port =8081
s.connect((host,port))
s.send(tuple_uart)

