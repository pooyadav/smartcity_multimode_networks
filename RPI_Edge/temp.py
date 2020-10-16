""" Simple program to test socket via UART """
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 8081
s.connect((host, port))
str_v = b'HelloWorldFromTemp\n'
#str_v = bytes('HelloWorldFromTemp', 'ascii') 
#str_v = bytes('HelloWorldFromTemp', 'utf-8')
#str_b = str_v.encode('UTF-8')
s.send(str_v)
buf = ""
while True:
#    temp = s.recv(1024)
    temp = s.recv(len(str_v))
    if '\n' in temp:
        buf = buf + temp
        buf.strip()
        print(buf)
    else:
        buf = buf + temp
