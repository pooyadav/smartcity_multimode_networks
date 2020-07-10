""" Function definition for connecting different networks"""
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


# Wifi_Creds
WIFI_SSID = "BTHub6-WK6Q-LS"
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

def connect_lora_otaa():
    """ Connect to LoRa and return lora and socket via OTAA auth method"""
    lora.join(activation=LoRa.OTAA, auth=(APP_EUI, APP_KEY), timeout=0)

    # wait until the module has joined the network
    i = 1
    while not lora.has_joined():
        i = i + 1
        time.sleep(2.5)
        print('Not yet joined...')
        if i == 5:
            print("Gave up on Lora; Network signal not strong")
            return None

    print("Finally Joined")

# Print Stats
    print("Lora.bandwidth is " + lora.Bandwidth())
    print("Lora.sf is " + lora.sf())
    print("lora.coding_rate is " + lora.coding_rate())
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
    uart = UART(1, baudrate=9600)
    uart.init(9600, bits=8, parity=None, stop=1)
#    send_mqtt("HelloWorld")
    while True:
        try:
            if uart.any() != 0:
                uart_msg = uart.readline()
                if uart_msg is not None:
#                    send_mqtt(uart_msg)
                    uart_msg = uart_msg.decode("utf-8")
#                    print("UART Message is " + str(type(uart_msg)) + str(uart_msg))
                    check_connection(uart_msg, s_lora, s_sigfox)
                    uart.write("Data sent\n")
        except:
            print("Keyboard Interrupt")
            raise
            break

def connect_nbiot():
    """ Connect to NB-IoT network"""
    lte.attach(band=20, apn="nb.inetd.gdsp")
    while not lte.isattached():
        print("LTE: Not attached yet")
        time.sleep(0.25)
    print("LTE: Attached")
    lte.connect()       # start a data session and obtain an IP address
    while not lte.isconnected():
        print("LTE: Not connected yet")
        time.sleep(0.25)
    print("LTE: Connected")

def check_connection(msg, s_lora, s_sigfox):
    """ Check which networks are connected and send data via that network """
#        check if wlan is connected
#       if connected great! If not check if nb-iot, lora, sigfox
    connected_wifi = wlan.isconnected()
#    connected_lte = lte.isconnected()
    connected_lte = False
    connected_lora = lora.has_joined()
    if connected_wifi:
        ## Send data using WiFi
        print("Data on WiFi")
        post_var(msg, "wifi")
    elif connected_lte:
        ## Send data using lte
        print("Data on LTE")
        post_var(msg, "lte")
    elif connected_lora:
        ## Send data using lora
        s_lora.send(msg)
        print("Data on Lora")
    else:
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

# Builds the json to send the request
def build_json(time, temp):
    try:
        time = 1234
        temp = 34
        data = {time,temp}
        return data
    except:
        return None

# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post_var(msg, medium):
    try:
        url = "http://8.209.93.91:8080/"
        url = url + medium
        headers = {"X-Auth-Token": "FiPy", "Content-Type": "application/json"}
        if msg is not None:
            print(msg)
            req = requests.post(url=url, headers=headers, data=msg)
            print (req.status_code)
            status_code = req.status_code
            req.close()
            return status_code
        else:
            print("WTF")
            pass
    except:
        print("Yahoo")
        raise
        pass

def main():
    """ Main function currently make calls to connect all networks and UART """
#    connect_wifi(WIFI_SSID, WIFI_PASS)
    s_lora = connect_lora_otaa()
    s_sigfox = connect_sigfox()
    connect_uart(s_lora, s_sigfox)

if __name__ == "__main__":
    main()
