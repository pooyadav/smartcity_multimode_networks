import time
import machine
import urequests as requests
from network import WLAN
from umqtt import MQTTClient
from machine import UART
from network import LoRa
from network import Sigfox
from network import LTE
import ubinascii
import pycom
import struct
import socket
import pycom
import _thread
import machine
rtc = machine.RTC()


# Wifi_Creds
WIFI_SSID = "BTHub6-WK6Q"
WIFI_PASS = "9XGDxfLnPvEq"
# Lora OTAA Key
# create an OTAA authentication parameters
APP_EUI = ubinascii.unhexlify('70B3D57ED0030B7E')
APP_KEY = ubinascii.unhexlify('02BEBE90D3FF4C1C26EBD71DDA585214')


#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html.
wlan = WLAN(mode=WLAN.STA)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
#lte = LTE()


# A function has been defined to be called in the main file to make it shorter
def connect_wifi(ssid, passwifi):
    """ Connect WiFi using provided ssid, password"""

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
    print("network not found")
    connect_wifi(ssid, passwifi)

def connect_sigfox():
    """ Connect to SigFox and return sigfox and socket"""

# Create a Sigfox socket
    sock_sigfox = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
    print("Hello3")
# make the socket blocking
    sock_sigfox.setblocking(True)
# Configure it as uplink
    sock_sigfox.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
# send some data
#    sock_sigfox.send("Hello SigFox")
#    print("Message sent on Sigfox")
    return sock_sigfox

def main():
    """ Main function currently make calls to connect all networks and UART """
    connect_wifi(WIFI_SSID, WIFI_PASS)
    rtc.ntp_sync("pool.ntp.org")
    time.timezone(3600)
    time.sleep(5)
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    s_sigfox = connect_sigfox()

    for x in range(1,13):
        msg = "A" * x
        print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*time.localtime()[:6]),end = '')
        start = time.time()
        s_sigfox.send(msg)
        stop = time.time()
        time_taken = stop - start
        print(",MSize:" + str(len(msg)) + ",Time:" + str(time_taken) + ",RB:")

if __name__ == "__main__":
    main()
