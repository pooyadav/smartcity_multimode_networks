#from gpiozero import CPUTemperature
import ast
import time
import socket
import select
import sys
import logging
import threading
import copy
from multiprocessing import Queue

# Creating a socket to connect to the UART
event = threading.Event()
stop_threads = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host ="localhost"
port =8081
s.connect((host,port))

inputs = [s]
outputs = [s]
message_queues = {}
message_queues[s] = Queue()
list_threads = []
stats = dict()

def stop_all_threads():
    print("in stop_all_threads") 
    global list_threads
    event.set()
    # Doing this because we are removing items from list and it's not safe!
    for i in range(0, len(list_threads)):
        thread = list_threads[i]
        thread.join()
        print("Thread Killed")
    list_threads.clear()
    event.clear()


def read_mfe(mfea):
    print("in read mfea") 
    # Assuming MFE is in format: 
    #MFEA:[{'PS': 40, 'N': 'SigFox', 'MF': 'Energy Usage', 'PE': 3600, 'CL': 0}, {'PS': 30, 'N': 'SigFox', 'MF': 'Body Temperature', 'PE': 30, 'CL': 0}, {'PS': 40000, 'N': 'Wi-Fi', 'MF': 'Bedroom Sensor', 'PE': 10, 'CL': 0}, {'PS': 80, 'N': 'LoRaWAN', 'MF': 'Bathroom Sensor', 'PE': 10, 'CL': 0}, {'PS': 40000, 'N': 'Wi-Fi', 'MF': 'Kitchen Sensor', 'PE': 10, 'CL': 0}, {'PS': 10, 'N': 'SigFox', 'MF': 'Front Door Sensor', 'PE': 30, 'CL': 1}, {'PS': 1000, 'N': 'LoRaWAN', 'MF': 'Fall Detection', 'PE': 10, 'CL': 0}, {'PS': 80, 'N': 'LoRaWAN', 'MF': 'Heart Monitoring', 'PE': 10, 'CL': 1}]
    #MFEA:[{'PS': 40, 'N': 'SigFox', 'MF': 'Energy Usage', 'PE': 3600, 'CL': 0}, {'PS': 30, 'N': 'SigFox', 'MF': 'Body Temperature', 'PE': 30, 'CL': 0}]
    

    ## Okies.. we have recieved the MFE allocations, let's first check whether there are existing threads? If so, let's stop them
    stop_all_threads()
    # Converting String into list of dict
    res = ast.literal_eval(mfea)
    
    # Extracting msgflow_name, cric_level, payload, period
    for item in res:
        msgflow_name = item["MF"]
        msgflow_crit_level = item["CL"]
        msgflow_payload_size = item["PS"]
        msgflow_period = item["PE"]
        create_stats(msgflow_name)

        print("Message Flow" + msgflow_name + " of crit level " + str(msgflow_crit_level) + " Period " + str(msgflow_period))
        msgflow_payload = "A" * msgflow_payload_size
        args_tuple = [event, msgflow_name, msgflow_crit_level, msgflow_period, msgflow_payload ]
        # Let's say we create msgflow payload here
        x = threading.Thread(target=write_data_uart, args=args_tuple)
        x.start()
        list_threads.append(x)


def create_stats(msgflow_name):
    sent_recv = {'sent': 0, 'recv': 0}
    if msgflow_name not in stats.keys():
        stats[msgflow_name] = sent_recv

def ack_message(msgflow_name):
    if msgflow_name in stats.keys():
        stats[msgflow_name]["recv"] = stats[msgflow_name]["recv"] + 1



def write_data_uart(event, msgflow_name, msgflow_crit_level, msgflow_period, msgflow_payload):
    """ Writing data on the UART with msgflow_name, msgflow_crit_level, msgflow_payload """
    # Let's say we want to send two messages
    for i in range(0, 2):
#    while True:
        # Check for Global Variable if threads need to stop
        if event.isSet(): 
            break        
        msg_uart = msgflow_name + "," + str(msgflow_crit_level) + "," + msgflow_payload + "\n"
        message_queues[s].put(msg_uart)
        print("Message written, sleeping")
        stats[msgflow_name]["sent"] = stats[msgflow_name]["sent"] + 1
        event.wait(5)


def connect_to_uart():

# Run a while loop, with socket select, socket check when there's a message from UART
# such as MFE allocations
    while True:

        # Wait for at least one of the sockets to be ready for processing
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for sock in readable:
            # Incoming message from UART
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from server')
                    sys.exit()
                else:
                    temp = data.decode('utf-8')
                    # Message Flow Allocation Message
                    if temp.startswith('MFEA'):
                        # Call the read_mfe function
                        print("In connect_to_uart")
                        temp2 = temp.split(":", 1)
                        read_mfe(temp2[1])

                    if temp.startswith('ACK'):
                        temp2 = temp.split(":",1)
                        msgflow_name = temp2[1].rstrip()
                        ack_message(msgflow_name)
                
                    if temp.startswith('STATS'):
                        print(stats)
                        


        for sock in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except:
                # No messages waiting so stop checking for writability.
    #            print("output queue for " + str(s.getpeername()) + " is empty")
                pass
    #            outputs.remove(s)
            else:
                temp = next_msg.split(",")
                print_msg = next_msg[0] + next_msg[1]

                print("sending " + str(print_msg.rstrip()) + " to " + str(s.getpeername()))
                next_msg = next_msg.encode('utf-8')
                s.send(next_msg)        
    

if __name__ == '__main__':
    
    connect_to_uart()