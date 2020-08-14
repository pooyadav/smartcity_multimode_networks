import time
import machine
import urequests as requests
from network import WLAN
from umqtt import MQTTClient
from machine import UART
from machine import Pin
#from network import LoRa
#from network import Sigfox
#from network import LTE
import ubinascii
import pycom
import struct
import socket
import pycom
import _thread
rtc = machine.RTC()


# Wifi_Creds
WIFI_SSID = "BTHub6-WK6Q"
WIFI_PASS = "9XGDxfLnPvEq"
# Lora OTAA Key
# create an OTAA authentication parameters
APP_EUI = ubinascii.unhexlify('70B3D57ED0030B7E')
APP_KEY = ubinascii.unhexlify('02BEBE90D3FF4C1C26EBD71DDA585214')


#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html.
time_init_start = time.time()
wlan = WLAN(mode=WLAN.STA,antenna=WLAN.EXT_ANT)
Pin('P12', mode=Pin.OUT)(True)
p=Pin('P12', mode=Pin.OUT)  #this pin used for antenna switching
time_init_stop = time.time()
time_scan_start = 0
time_scan_stop = 0
time_connect_start = 0
time_connect_stop = 0

#sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
#lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
#lte = LTE()


# A function has been defined to be called in the main file to make it shorter
def connect_wifi(ssid, passwifi):
    """ Connect WiFi using provided ssid, password"""
    time_init_start = time.time()
    wlan = WLAN(mode=WLAN.STA,antenna=WLAN.EXT_ANT)
    time_init_stop = time.time()
    global time_scan_start
    global time_scan_stop
    global time_connect_start
    global time_connect_stop

#    print("Trying to connect to " + ssid)
#    wlan.antenna(WLAN.INT_ANT);
    wlan.antenna(WLAN.EXT_ANT);
    #print(wlan.antenna())
    time_scan_start = time.time()
    nets = wlan.scan()
    time_scan_stop = time.time()
    for net in nets:
#        print(net.ssid)
        if net.ssid == ssid:
#            print('Network found!')
            time_connect_start = time.time()
            wlan.connect(net.ssid, auth=(net.sec, passwifi), timeout=10000)
            while not wlan.isconnected():
                print('.',end='')
                time.sleep(1)
                machine.idle() # save power while waiting
#            print('WLAN connection succeeded!')
            time_connect_stop = time.time()
            return True
    print("network not found")
    connect_wifi(ssid, passwifi)

def measure_wifi():
    time_init = time_init_stop - time_init_start
    time_scan = time_scan_stop - time_scan_start
    time_connect = time_connect_stop - time_connect_start
    time_disconnect_start = time.time()
    wlan.disconnect()
    time_disconnect_stop = time.time()
    time_disconnect = time_disconnect_stop - time_disconnect_start
    time_deinit_start = time.time()
    wlan.deinit()
    time_deinit_stop = time.time()
    time_deinit = time_deinit_stop - time_deinit_start
    print("\nInit:" + str(time_init) + " Scan:" + str(time_scan) + " Connect:" + str(time_connect) + " Disconnect:" + str(time_disconnect) + " Dinit" + str(time_deinit))


def main():
    """ Main function currently make calls to connect all networks and UART """
    while not wlan.isconnected():
        connect_wifi(WIFI_SSID, WIFI_PASS)
        measure_wifi()

    rtc.ntp_sync("pool.ntp.org")
    time.timezone(3600)
    rtc.ntp_sync("pool.ntp.org")


if __name__ == "__main__":
    main()
