""" Function definition for connecting different networks"""
import time
import machine
import urequests as requests
from network import WLAN
from umqtt import MQTTClient
from network import LoRa
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
APP_KEY = ubinascii.unhexlify('F7C66D9A0DEED29286E2FE328B0BB215')


#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html.
wlan = WLAN(mode=WLAN.STA)

init_lora_start=time.time()
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868,tx_power=14, sf=12)
init_lora_stop=time.time()

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

def connect_lora_otaa():
    """ Connect to LoRa and return lora and socket via OTAA auth method"""
    msg = "A"*51
    join_lora_start=time.time()
    lora.join(activation=LoRa.OTAA, auth=(APP_EUI, APP_KEY), timeout=0,dr=1)

    # wait until the module has joined the network
    i = 1
    while not lora.has_joined():
        i = i + 1
        time.sleep(1)
        print('.',end='')
        if i == 200:
            print("Gave up on Lora; Network signal not strong")
            return None
    join_lora_stop=time.time()
    print("Finally Joined")

# Print Stats
    print("Lora.bandwidth:" + str(lora.bandwidth()) + ",Lora.sf:" + str(lora.sf()) + ",lora.coding_rate:" + str(lora.coding_rate()))
# create a LoRa socket
    sock_lora_start=time.time()
    sock_lora = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
    sock_lora.setsockopt(socket.SOL_LORA, socket.SO_DR, 1)
# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
    sock_lora.setblocking(True)
# send some data
#    sock_lora.send(bytes([0x01, 0x02, 0x03]))
# make the socket non-blocking
# (because if there's no data received it will block forever...)
    sock_lora.setblocking(False)
    sock_lora_stop=time.time()
    init_time = init_lora_stop - init_lora_start
    join_time = join_lora_stop - join_lora_start
    sock_time = sock_lora_stop - sock_lora_start




    print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*time.localtime()[:6]),end = '')
    send_starttime = time.time()
#    sock_lora.send(msg)
    send_stoptime = time.time()
    send_time = send_stoptime - send_starttime
    print(",InitTime:" + str(init_time) +",JoinTime:"+str(join_time)+",sock_time:" + str(sock_time)+",send_Time:"+str(send_time))
# get any data received (if any...)
    data = sock_lora.recv(64)

    return sock_lora

def main():
    """ Main function currently make calls to connect all networks and UART """
    connect_wifi(WIFI_SSID, WIFI_PASS)
    rtc.ntp_sync("pool.ntp.org")
    time.timezone(3600)
    time.sleep(5)
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    s_lora = connect_lora_otaa()
    for i in range(1,11):
        connect_lora_otaa()
        time.sleep(5)


if __name__ == "__main__":
    main()
