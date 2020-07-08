""" Function definition for connecting different networks"""
import time
import machine
from network import WLAN

#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html.
wlan = WLAN(mode=WLAN.STA)

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

    obj_sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
# Create a Sigfox socket
    sock_sigfox = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
    print("Hello3")
# make the socket blocking
    sock_sigfox.setblocking(True)
# Configure it as uplink
    sock_sigfox.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
# send some data
    sock_sigfox.send("Hello SigFox")
    print("Message sent on Sigfox")
    return obj_sigfox, sock_sigfox

def connect_lora_otaa():
    """ Connect to LoRa and return lora and socket via OTAA auth method"""
    obj_lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    obj_lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not obj_lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

    print("Finally Joined")

# Print Stats
    print("Lora.bandwidth is " + obj_lora.Bandwidth())
    print("Lora.sf is " + obj_lora.sf())
    print("lora.coding_rate is " + obj_lora.coding_rate())
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
    return obj_lora, sock_lora


def connect_lora_abp():
    """ Connect to LoRa and return lora and socket via ABP auth method"""
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

def connect_uart():
    """ Connect to UART Pins P3/P4 and send data to the cloud"""
    uart = UART(1, baudrate=115200)
    uart.init(115200, bits=8, parity=None, stop=1)
#    send_mqtt("HelloWorld")
    while True:
        try:
            if uart.any() != 0:
                uart_msg = uart.readline()
                if uart_msg is not None:
#                    send_mqtt(uart_msg)
                    check_connection()
                    uart.write("Data sent\n")
        except:
            print("Keyboard Interrupt")
            raise
            break

def connect_nbiot():
    """ Connect to NB-IoT network"""
    obj_lte = LTE()
    obj_lte.attach(band=20, apn="nb.inetd.gdsp")
    while not lte.isattached():
        print("LTE: Not attached yet")
        time.sleep(0.25)
    print("LTE: Attached")
    obj_lte.connect()       # start a data session and obtain an IP address
    while not obj_lte.isconnected():
        print("LTE: Not connected yet")
        time.sleep(0.25)
    print("LTE: Connected")

def check_connection():
    """ Check which networks are connected and send data via that network """
    i = 1
    while i < 6:
#        check if wlan is connected
#       if connected great! If not check if nb-iot, lora, sigfox
        connected_wifi = wlan.isconnected()
        connected_lte = lte.isconnected()
        connected_lora = lora.has_joined()
        if connected_wifi:
            ## Send data using WiFi
            print("Data on WiFi")
        elif connected_lte:
            ## Send data using lte
            print("Data on LTE")
        elif connected_lora:
            ## Send data using lora
            print("Data on Lora")
        else:
            # Send only important data on SigFox (12bytes)
            print("Data sent on SigFox")
