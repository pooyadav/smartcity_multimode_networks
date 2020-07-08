import pycom
import time
import struct
from network import Sigfox
from umqtt import MQTTClient
from machine import UART
from network import LoRa
import socket
import ubinascii

# Wifi_Creds
wifi_ssid = "BTHub6-WK6Q-LS"
wifi_pass = "9XGDxfLnPvEq"
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


def main():
    connect_wifi(wifi_ssid, wifi_pass)
    lora, s_lora = connect_lora_otaa()
    sigfox, s_sigfox = connect_sigfox()
    connect_UART()

if __name__ == "__main__":
    main()
