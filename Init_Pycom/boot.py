import machine
from network import WLAN
import time

#The code is taken from https://docs.pycom.io/chapter/tutorials/all/wlan.html. from the section Connecting to a Router.
wlan = WLAN(mode=WLAN.STA)

# A function has been defined to be called in the main file to make it shorter and more efficient
def connect_wifi(ssid,passwifi):

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
    print ("network not found")
    connect_wifi(ssid,passwifi)

def connect_sigfox():

    sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
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
    return sigfox, s

def connect_lora_otaa():
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

    print ("Finally Joined")

# Print Stats
    print("Lora.bandwidth is " + lora.Bandwidth())
    print("Lora.sf is " + lora.sf())
    print("lora.coding_rate is " + lora.coding_rate())
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
    return lora, s


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
    uart = UART(1, baudrate=115200)
    uart.init(115200, bits=8, parity=None, stop=1)
#    send_mqtt("HelloWorld")
    while True:
        try:
            if (uart.any() != 0):
                uart_msg = uart.readline()
                if uart_msg != None:
#                    send_mqtt(uart_msg)
                    check_connection()
                    uart.write("Data sent\n")
        except:
            print ("Keyboard Interrupt")
            raise
            break

def connect_nbiot():
    lte = LTE()
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

def check_connection():
    i = 1
    while i < 6:
#        check if wlan is connected
#       if connected great! If not check if nb-iot is connected, if not check lora is connected, if not SigFox
        connected_wifi = wlan.isconnected()
        connected_lte = lte.isconnected()
        connected_lora = lora.has_joined()
        if connected_wifi == True:
            ## Send data using WiFi
            print("Data on WiFi")
        elif connected_lte == True:
            ## Send data using lte
            print("Data on LTE")
        elif connected_lora != True:
            ## Send data using lora
            print("Data on Lora")
        else:
            # Send only important data on SigFox (12bytes)
            print ("Data sent on SigFox")
