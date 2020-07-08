""" Main program for Multi-modal network POC """
import time
import struct
import socket
import pycom
from umqtt import MQTTClient
from machine import UART
from network import LoRa
from network import Sigfox
import ubinascii

# Wifi_Creds
WIFI_SSID = "BTHub6-WK6Q-LS"
WIFI_PASS = "9XGDxfLnPvEq"
# Lora OTAA Key
# create an OTAA authentication parameters
APP_EUI = ubinascii.unhexlify('70B3D57ED0030B7E')
APP_KEY = ubinascii.unhexlify('02BEBE90D3FF4C1C26EBD71DDA585214')

def sub_cb(topic, msg):
    """ Function to Not sure Print Message """
    print(msg)

def send_mqtt(mqtt_msg):
    """ Function to Send MQTT Message """
    client = MQTTClient("PyCom-LoPy", "node-0003", port=1884)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic="HelloWorld/HelloUART")
    client.publish(topic="HelloWorld/HelloUART", msg=mqtt_msg)
    client.check_msg()

def main():
    """ Main function currently make calls to connect all networks and UART """
    connect_wifi(WIFI_SSID, WIFI_PASS)
    lora, s_lora = connect_lora_otaa()
    sigfox, s_sigfox = connect_sigfox()
    connect_UART()

if __name__ == "__main__":
    main()
