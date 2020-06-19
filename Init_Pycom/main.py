import pycom
import time
import struct
from umqtt import MQTTClient
from machine import UART
from network import LoRa
from network import Sigfox
import socket
import socket
import ubinascii

# Wifi_Creds
wifi_ssid = "XXXXXXXXX"
wifi_pass = "XXXXXXXXX"
# Lora OTAA Key
# create an OTAA authentication parameters
app_eui = ubinascii.unhexlify('70B3D57ED0030B7E')
app_key = ubinascii.unhexlify('02BEBE90D3FF4C1C26EBD71DDA585214')

def sub_cb(topic, msg):
   print(msg)

def send_mqtt(mqtt_msg):
    client = MQTTClient("PyCom-LoPy", "node-0003", port=1884)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic="HelloWorld/HelloUART")
    client.publish(topic="HelloWorld/HelloUART", msg=mqtt_msg)
    client.check_msg()

def connect_sigfox():
    sigfox = Sigfox(mode=Sigfox.SIGFOX,rcz=Sigfox.RCZ1)
# Create a Sigfox socket
    s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
    print("Hello3")
# make the socket blocking
    s.setblocking(True)
# Configure it as uplink
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

# send some data
    s.send("Hello SigFox")
    print ("Message sent on Sigfox")

def connect_lora_otaa():
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

    print ("Finally Joined")

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


def connect_lora_abp():
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

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

def connect_UART():
    uart = UART(0, baudrate=9600)
    uart.init(9600, bits=8, parity=None, stop=1)
    send_mqtt("HelloWorld")
    while True:
        try:
            if (uart.any() != 0):
                uart_msg = uart.readline()
                if uart_msg != None:
                    send_mqtt(uart_msg)
                    uart.write("Data sent\n")
        except:
            print ("Keyboard Interrupt")
            raise
            breakin

def main():
#    connect_wifi(wifi_ssid, wifi_pass)
#    connect_UART()
#    connect_lora_otaa()
    connect_sigfox()

if __name__ == "__main__":
    main()
