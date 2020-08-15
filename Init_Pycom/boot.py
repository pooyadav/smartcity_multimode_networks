from network import LTE
import time
import utime
import socket
import machine
import uping
rtc = machine.RTC()
result3 = ""
lte = LTE()

#now we can safely machine.deepsleep()
def connect_lte():
    global result3


    start_resettime = time.time()
#    lte.reset()
    stop_resettime = time.time()
    start_inittime = time.time()
    lte = LTE()
    lte.init()
    stop_inittime = time.time()

    start_attachtime = time.time()
    lte.attach(band=20, apn="pycom.io")
    #print("attaching..",end='')
    while not lte.isattached():
        print('A',end='')
        time.sleep(0.25)

    #    print('.',end='')
    #    print(lte.send_at_cmd('AT!="fsm"'))         # get the System FSM
#    print("attached!")
    stop_attachtime = time.time()

    start_connecttime=time.time()
    lte.connect()
    #print("connecting [##",end='')
#    print("connect init")
    while not lte.isconnected():
        print('C',end='')
        time.sleep(0.25)
    #    print('#',end='')
        #print(lte.send_at_cmd('AT!="showphy"'))
    #    print(lte.send_at_cmd('AT!="fsm"'))
    #print("] connected!")
#    print("connected!")
    stop_connecttime=time.time()

    #result = socket.getaddrinfo('pycom.io', 80)

    start_disconnecttime=time.time()
#    lte.disconnect()
    stop_disconnectime=time.time()

    start_deinittime=time.time()
#    lte.deinit()
    stop_deinittime=time.time()

    time_lteinit = stop_inittime - start_inittime
    time_lteattach = stop_attachtime - start_attachtime
    time_lteconnect = stop_connecttime - start_connecttime
    time_ltedisconnect = stop_disconnectime - start_disconnecttime
    time_ltedeinit = stop_deinittime - start_deinittime
    time_ltereset = stop_resettime - start_resettime

    result2 = ("\nCurrent Time:" + str(utime.time()) + ",LTE_Reset:" + str(time_ltereset) + ",LTE_Init:" + str(time_lteinit) + ",LTE_Attach:" + str(time_lteattach) + ",LTE_Connect:" + str(time_lteconnect) + ",LTE_Disconnect:" + str(time_ltedisconnect) + ",LTE DeInit: " + str(time_ltedeinit))
    print (result2 )
    result3 = result3 + result2

def main():
    """ Main function currently make calls to connect all networks and UART """
    connect_lte()
#    uping.ping('10.200.0.1')

if __name__ == "__main__":
    main()
