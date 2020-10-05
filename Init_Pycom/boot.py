""" Function definition for connecting different networks"""
import utime
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
from mnm.multi_network_management import multi_network_management
from mnm.msgflow import MessageFlow
from mnm.network_algo import Network
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
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868,tx_power=14)
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
    lora.join(activation=LoRa.OTAA, auth=(APP_EUI, APP_KEY), timeout=0)

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
#    print("Lora.bandwidth:" + str(lora.bandwidth()) + ",Lora.sf:" + str(lora.sf()) + ",lora.coding_rate:" + str(lora.coding_rate()))
# create a LoRa socket
    sock_lora_start=time.time()
    sock_lora = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
    sock_lora.setsockopt(socket.SOL_LORA, socket.SO_DR,0)
# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
    sock_lora.setblocking(True)
# send some data
#    sock_lora.send(bytes([0x01, 0x02, 0x03]))
# make the socket non-blocking
# (because if there's no data received it will block forever...)
    sock_lora.setblocking(False)
    sock_lora_stop=time.time()
    print("Lora.bandwidth:" + str(lora.bandwidth()) + ",Lora.sf:" + str(lora.sf()) + ",lora.coding_rate:" + str(lora.coding_rate()))
    init_time = init_lora_stop - init_lora_start
    join_time = join_lora_stop - join_lora_start
    sock_time = sock_lora_stop - sock_lora_start



    for i in range(1,11):
        print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*time.localtime()[:6]),end = '')
        send_starttime = utime.ticks_us()
        sock_lora.send(msg)
        send_stoptime = utime.ticks_us()
        send_time = send_stoptime - send_starttime
        print(",InitTime:" + str(init_time) +",JoinTime:"+str(join_time)+",sock_time:" + str(sock_time)+",send_Time:"+str(send_time))
        time.sleep(10)
# get any data received (if any...)
    data = sock_lora.recv(64)

    return sock_lora

def check_allocations():
    falld = MessageFlow("Fall Detection", 0, 1000, 10)
    falld.set_crit_level(1, 40, 20)
    falld.set_crit_level(2, 10, 60)

    healthm = MessageFlow("Heart Monitoring", 0, 1000, 5)
    healthm.set_crit_level(1, 80, 10)
    healthm.set_crit_level(2, 10, 20)

    bodyt = MessageFlow("Body Temperature", 0, 30, 30)
    bodyt.set_crit_level(1, 10, 120)

    bedsens = MessageFlow("Bedroom Sensor", 0, 40000, 10)
    bedsens.set_crit_level(1, 10, 30)

    bathsens = MessageFlow("Bathroom Sensor", 0, 80, 10)
    bathsens.set_crit_level(1, 10, 30)

    kitsens = MessageFlow("Kitchen Sensor", 0, 40000, 10)
    kitsens.set_crit_level(1, 10, 30)

    frontsens = MessageFlow("Front Door Sensor", 0, 40000, 10)
    frontsens.set_crit_level(1, 10, 30)

    enermon = MessageFlow("Energy Usage", 0, 40, 3600)

    # Let's say network 1 has 8000 bps bandwidth
    network1 = Network("Wi-Fi", True, 8000, -1, -1)
    network4 = Network("LoRaWAN", True, 220, 222, 144)
    network2 = Network("SigFox", True, 6, 12, 144)
    network3 = Network("LTE-M", True, 10, 12, 144)
    mnm = multi_network_management()
    mnm.add_msgflow(falld)
    mnm.add_msgflow(healthm)
    mnm.add_msgflow(bodyt)
    mnm.add_msgflow(bedsens)
    mnm.add_msgflow(bathsens)
    mnm.add_msgflow(kitsens)
    mnm.add_msgflow(frontsens)
    mnm.add_msgflow(enermon)
    mnm.add_network(network1)
    mnm.add_network(network4)
    mnm.add_network(network2)


    mnm.set_decreasing(False)
    mnm.set_best_fit()

    mnm.perform_inverted_allocation()
    mnm.print_all_allocation()
    mnm.print_unallocated_elements()
    print("Allocated Percentage is " + str(mnm.get_allocated_percentage()))
    print("Average Criticality is " + str(mnm.get_avg_criticality()))


def main():
    """ Main function currently make calls to connect all networks and UART """
    connect_wifi(WIFI_SSID, WIFI_PASS)
    rtc.ntp_sync("pool.ntp.org")
    time.timezone(3600)
    time.sleep(5)
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    #s_lora = connect_lora_otaa()
    check_allocations()

if __name__ == "__main__":
    main()
