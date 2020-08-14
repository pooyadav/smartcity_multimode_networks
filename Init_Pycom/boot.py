from network import LTE
import time
import utime
import socket
import machine
rtc = machine.RTC()

start_inittime = time.time()
lte = LTE()
lte.init()
stop_inittime = time.time()

start_attachtime = time.time()
lte.attach(band=20, apn="pycom.io")
#print("attaching..",end='')
while not lte.isattached():
    print("Attaching")
    time.sleep(0.25)

#    print('.',end='')
#    print(lte.send_at_cmd('AT!="fsm"'))         # get the System FSM
print("attached!")
stop_attachtime = time.time()

start_connecttime=time.time()
lte.connect()
#print("connecting [##",end='')
print("connect init")
while not lte.isconnected():
    print("Connecting")
    time.sleep(0.25)
#    print('#',end='')
    #print(lte.send_at_cmd('AT!="showphy"'))
#    print(lte.send_at_cmd('AT!="fsm"'))
#print("] connected!")
print("connected!")
stop_connecttime=time.time()

result = socket.getaddrinfo('pycom.io', 80)

start_disconnecttime=time.time()
lte.disconnect()
stop_disconnectime=time.time()

start_deinittime=time.time()
lte.deinit()
stop_deinittime=time.time()

time_lteinit = stop_inittime - start_inittime
time_lteattach = stop_attachtime - start_attachtime
time_lteconnect = stop_connecttime - start_connecttime
time_ltedisconnect = stop_disconnectime - start_disconnecttime
time_ltedeinit = stop_deinittime - start_deinittime

result2 = ("Current Time is " + str(utime.time()) + " LTE_Init: " + str(time_lteinit) + " LTE_Attach: " + str(time_lteattach) + " LTE_Connect: " + str(time_lteconnect) + " LTE_Disconnect: " + str(time_ltedisconnect) + " LTE DeInit: " + str(time_ltedeinit))
print (result2 )

#now we can safely machine.deepsleep()
