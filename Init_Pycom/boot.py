import machine
from network import WLAN
import time

#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html. from the section Connecting to a Router.
wlan = WLAN(mode=WLAN.STA)

# A function has been defined to be called in the main file to make it shorter and more efficient
def connect_wifi(ssid,passwifi):

    print("Trying to connect to " + ssid)
    # wlan.antenna(WLAN.EXT_ANT)
    nets = wlan.scan()
    for net in nets:
        print(net.ssid)
        if net.ssid == ssid:
            print('Network found!')
            wlan.connect(net.ssid, auth=(net.sec, passwifi), timeout=10000)
            while not wlan.isconnected():
                print("trying to connect")
                time.sleep(1)
                machine.idle() # save power while waiting
            print('WLAN connection succeeded!')
            return True
    print ("network not found")
    connect_wifi(ssid,passwifi)
