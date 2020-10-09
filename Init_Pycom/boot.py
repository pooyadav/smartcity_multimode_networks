""" Function definition for connecting different networks"""
#import urandom
import os
import sys
import struct
import socket
from network import WLAN
from network import Sigfox
from network import LTE
from network import LoRa
#from umqtt import MQTTClient
import ubinascii
import urequests as requests
import utime
import _thread
import machine
from machine import UART
from mnm.multi_network_management import multi_network_management
from mnm.msgflow import MessageFlow
from mnm.network_algo import Network
rtc = machine.RTC()
uart = UART(1, 9600)                         # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters
mnm = multi_network_management()



# Wifi_Creds
WIFI_SSID = "BTHub6-WK6Q"
WIFI_PASS = "9XGDxfLnPvEq"
# Lora OTAA Key
# create an OTAA authentication parameters
APP_EUI = ubinascii.unhexlify('70B3D57ED0030B7E')
APP_KEY = ubinascii.unhexlify('43FB05A51AA73EC05511F936279DEB4E')


#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html.
wlan = WLAN(mode=WLAN.STA)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
lte = LTE()

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
                print('W', end='')
                utime.sleep(1)
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

def connect_lora_otaa():
    """ Connect to LoRa and return lora and socket via OTAA auth method"""
    lora.join(activation=LoRa.OTAA, auth=(APP_EUI, APP_KEY), timeout=0)

    # wait until the module has joined the network
    i = 1
    while not lora.has_joined():
        i = i + 1
        utime.sleep(2.5)
        print('L', end='')
        if i == 20:
            print("Gave up on Lora; Network signal not strong")
            return None

    print("Finally Joined")

# Print Stats
    print("Lora.bandwidth is " + str(lora.bandwidth()))
    print("Lora.sf is " + str(lora.sf()))
    print("lora.coding_rate is " + str(lora.coding_rate()))
# create a LoRa socket
    sock_lora = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
    sock_lora.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
    sock_lora.setblocking(True)
# send some data
    sock_lora.send(bytes([0x01, 0x02, 0x03]))
# make the socket non-blocking
# (because if there's no data received it will block forever...)
    sock_lora.setblocking(False)

# get any data received (if any...)
    data = sock_lora.recv(64)
    print(data)
    return sock_lora


def connect_lora_abp():
    """ Connect to LoRa and return lora and socket via ABP auth method"""
# create an ABP authentication params
    dev_addr = struct.unpack(">l", ubinascii.unhexlify('26001910'))[0]
    nwk_swkey = ubinascii.unhexlify('6AB31CFB360ACF58F327FC1CAD62F00C')
    app_swkey = ubinascii.unhexlify('84F85AB9B80943F7CF491D55EDEE1D56')

# join a network using ABP (Activation By Personalization)
    lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

# send some data
    s.send(bytes([0x01, 0x02, 0x03]))

# make the socket non-blocking
# (because if there's no data received it will block forever...)
    s.setblocking(False)

# get any data received (if any...)
    data = s.recv(64)
    print(data)

def connect_uart(s_lora, s_sigfox):
    """ Connect to UART Pins P3/P4 and send data to the cloud"""
    while True:
        try:
            if uart.any() != 0:
                uart_msg = uart.readline()
                if uart_msg is not None:
#                    send_mqtt(uart_msg)
                    uart_msg = uart_msg.decode("utf-8")
                    print("UART Message is " + str(type(uart_msg)) + str(uart_msg))
                    check_connection(uart_msg, s_lora, s_sigfox)
#                    uart.write("Data sent\n")
        except:
            print("Keyboard Interrupt")
            raise

def connect_nbiot():
    """ Connect to NB-IoT network"""
    lte.init()
    lte.attach(band=20, apn="pycom.io")
    while not lte.isattached():
        print('A', end='')
        utime.sleep(0.25)
    print("LTE: Attached")
    lte.connect()       # start a data session and obtain an IP address
    while not lte.isconnected():
        print('C', end='')
        utime.sleep(0.25)
    print("LTE: Connected")

def check_connection(msg_array, s_lora, s_sigfox):
    """ Check which networks are connected and send data via that network """
#        check if wlan is connected
#       if connected great! If not check if nb-iot, lora, sigfox
    # Splitting the message to get the flow name, crit_level and msg.
    temp_msg = msg_array.split(",")
    msgflow_name = temp_msg[0]
    msgflow_crit_level = temp_msg[1]
    msg = temp_msg[2]
    print(msgflow_name, msgflow_crit_level)
    bin_name = mnm.get_network_bin(msgflow_name, int(msgflow_crit_level))
    print("Check Connection?" + str(bin_name or 'Not Allocated'))
    connected_wifi = wlan.isconnected()
#    connected_lte = lte.isconnected()
    connected_lte = False
    connected_lora = lora.has_joined()
    if bin_name == "Wi-Fi" and connected_wifi:
        ## Send data using WiFi
        print("Data on WiFi")
        post_var(msg, "wifi")
    elif bin_name == "LTE-M" and connected_lte:
        ## Send data using lte
        print("Data on LTE")
        post_var(msg, "lte")
    elif bin_name == "LoRaWAN" and connected_lora:
        ## Send data using lora
        s_lora.send(msg)
        print("Data on Lora")
    elif bin_name == "SigFox":
        # Send only important data on SigFox (12bytes)
        if len(msg) > 12:
        # Assuming data is currently epochtime:cputime like 1594329236:66.705 which is 17 bytes.
        #Removing last two digit of epochtime (replace it with 00 at the server and removing : and . we make it to 12 bytes)
        # Reduced to 1594329236:66.705 to 159432926670
            temp_msg = msg
            temp_epoch = temp_msg.split(':')[0]
            temp_cputemp = temp_msg.split(':')[1]
            temp_epoch2 = temp_epoch[:-2]
            temp_cputemp2 = temp_cputemp.replace(".", "")
            temp_cputemp3 = temp_cputemp2[:-1]
            msg = temp_epoch2 + temp_cputemp3
        s_sigfox.send(msg)
        print("Data sent on SigFox")

# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post_var(msg, medium):
    """ Post the message via HTTP Post to the InfluxDB Server """
    try:
        url = "http://8.209.93.91:8080/"
        url = url + medium
        headers = {"X-Auth-Token": "FiPy", "Content-Type": "application/json"}
        if msg is not None:
            print(msg)
            req = requests.post(url=url, headers=headers, data=msg)
            print(req.status_code)
            status_code = req.status_code
            req.close()
            return status_code
        print("WTF: Error Message not sent")
    except:
        print("Yahoo")
        raise

def check_connection_thread(msg, s_lora, s_sigfox):
    """ Check which networks are connected and send data via that network """
#        check if wlan is connected
#       if connected great! If not check if nb-iot, lora, sigfox
    print("Hello World")
    args_tuple = [msg]
#    _thread.start_new_thread(thread_send_wifi, args_tuple)
#    _thread.start_new_thread(thread_send_lte, args_tuple)
    s_lora.send("HelloWorld")
    args_tuple = [msg, s_lora]
    _thread.start_new_thread(thread_send_lora, args_tuple)
    args_tuple = [msg, s_sigfox]
#    _thread.start_new_thread(thread_send_sigfox, args_tuple)
    print("Bye World")


def thread_send_wifi(msg):
    """ Thread Send the msg via WiFi """
    if wlan.isconnected():
        post_var(msg, "wifi")
    else:
        print("WiFi not connected")

def thread_send_lte(msg):
    """ Thread send the msg via LTE """
    if lte.isconnected():
        post_var(msg, "lte")
    else:
        print("LTE not connected")

def thread_send_lora(msg, s_lora):
    """ Thread send the msg via LoRaWAN """
    if lora.has_joined():
        s_lora.send(msg)
        print("Message sent on lora")
    else:
        print("Lora not connected")

def thread_send_sigfox(msg, s_sigfox):
    """ Thread send the msg via SigFox """
    # Send only important data on SigFox (12bytes)
    if len(msg) > 12:
        # Assuming data is currently epochtime:cputime like 1594329236:66.705 which is 17 bytes.
        #Removing last two digit of epochtime (replace it with 00 at the server and removing : and . we make it to 12 bytes)
        # Reduced to 1594329236:66.705 to 159432926670
        temp_msg = msg
        temp_epoch = temp_msg.split(':')[0]
        temp_cputemp = temp_msg.split(':')[1]
        temp_epoch2 = temp_epoch[:-2]
        temp_cputemp2 = temp_cputemp.replace(".", "")
        temp_cputemp3 = temp_cputemp2[:-1]
        msg = temp_epoch2 + temp_cputemp3
        s_sigfox.send(msg)
        print("Data sent on SigFox")
    else:
        s_sigfox.send(msg)

def write_data_uart(msgflow_name, msgflow_crit_level, msgflow_period, msgflow_payload):
    """ Writing data on the UART with msgflow_name, msgflow_crit_level, msgflow_payload """
    # Let's say we want to send two messages
    for i in range(0, 1):
        msg_uart = msgflow_name + "," + str(msgflow_crit_level) + "," + "A" * msgflow_payload
        #print(msg_uart)
        uart.write(msg_uart)
        print("Message written, sleeping")
        utime.sleep(msgflow_period)


def generate_random_data():
    """ Generating random data for each message flow defined """
    # Reading all the message flows
    for msgflow in mnm.list_msgflows:
        # Reading number of crit_levels in the Message Flow i.num_crit_level
        # Selecting a random crit_level, this may or may not be defined
        rand_crit_level = (int.from_bytes(os.urandom(1), sys.byteorder)) % (msgflow.num_crit_level - 1)
        # Try to get the MsgFlow which has a certain criticality defined
        while not msgflow.has_criticality(rand_crit_level):
            rand_crit_level = (int.from_bytes(os.urandom(1), sys.byteorder)) % (msgflow.num_crit_level - 1)
            # print("I am inside")
            # print(rand_crit_level)
        msgflow_name = msgflow.get_name()
        msgflow_payload = msgflow.get_payload(rand_crit_level)
        msgflow_period = msgflow.get_period(rand_crit_level)
        msgflow_crit_level = rand_crit_level
        #print(msgflow_name, msgflow_period, msgflow_payload)
        args_tuple = [msgflow_name, msgflow_crit_level, msgflow_period, msgflow_payload]
        # Start a new thread to send the message
        _thread.start_new_thread(write_data_uart, args_tuple)
        #write_data_uart(msgflow_name, msgflow_period, msgflow_payload)

def check_allocations():
    """ Setting up the message flows and the networks """
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
#    mnm = multi_network_management()
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
    utime.timezone(3600)
    utime.sleep(5)
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    rtc.ntp_sync("pool.ntp.org")
    s_lora = connect_lora_otaa()
    s_sigfox = connect_sigfox()
    if not wlan.isconnected():
        connect_wifi(WIFI_SSID, WIFI_PASS)
    if wlan.isconnected():
        print("Wi-Fi is connected")
    args_tuple = [s_lora, s_sigfox]
    check_allocations()
    _thread.start_new_thread(connect_uart, args_tuple)
    if wlan.isconnected():
        print("Wi-Fi is connected")
    else:
        print("Wi-Fi got disconnected")
    print("Everything is a thread")
    #generate_random_data()

if __name__ == "__main__":
    main()
