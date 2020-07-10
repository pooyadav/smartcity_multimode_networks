""" Main program for Multi-modal network POC """

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
#    connect_wifi(WIFI_SSID, WIFI_PASS)
#    s_lora = connect_lora_otaa()
#    s_sigfox = connect_sigfox()
#    connect_uart()

if __name__ == "__main__":
    main()
