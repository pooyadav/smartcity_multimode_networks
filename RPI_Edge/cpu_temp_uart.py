""" Module to run on Raspberry Pi to simulate Message Flow sending messages to UART """
import ast
import socket
import select
import sys
import threading
from multiprocessing import Queue


# Using threading.events to stop the threads when new Message Flow Allocation is received
event = threading.Event()

# Creating a socket to connect to the UART
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 8081
s.connect((host, port))

# Defining inputs, outputs, message queues for using Select with Socket
inputs = [s]
outputs = [s]
message_queues = {}
message_queues[s] = Queue()
# List to store the threads
list_threads = []
# Dict to store the stats of the MsgFlows
# Stores MsgFlow Name and how many packets has been sent and ack received
stats = dict()

def read_socket(sock):
    """ Function to read the socket until newline or the length has been reached from header """

    while True:
        data = ""
        size = len(data)

        while True:
            try:
                byte = sock.recv(1024)
                new_line = ["\n", "\r"]
                if byte is not None:
                    if byte not in new_line:
                        print("Len of byte is " + str(len(byte)))
                        if len(byte) == 1:
                            ":".join("{:02x}".format(ord(c)) for c in str(byte))
                        byte = byte.decode('UTF-8')
                        data += byte
                if data.startswith(':ML:'):
                #Setting ML length to be in format of :ML:500
                    temp = data.split(",", 1)
                    temp2 = temp[0].split(":")
                    msglen = int(temp2[2])
                    size = msglen
            except:
                print("Keyboard Interrupt")
                raise

            if not data:
                print("ERROR: No data received")
                return False
            # Newline terminates the read request
            if data.endswith("\n"):
                break
            # Sometimes a newline is missing at the end
            # If this round has the same data length as previous, we're done
            if size == len(data):
                break
            size = len(data)
        # Remove trailing newlines
        if data.startswith(':ML:'):
        #Setting ML length to be in format of :ML:500
            temp = data.split(",", 1)
            data = temp[1]
            data = data.rstrip("\r\n")
            data = data.rstrip("\n")
#        print("Final Message from read_uart is " + data)
        return data.encode("UTF-8")


def stop_all_threads():
    """ Function to stop the active threads, signal event.set and perform thread.join """
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
    """ Function to read MFE Allocation in the below format, extract each MF Allocation and create a thread to send message to UART """
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
        # Creating a entry into the stats dict
        create_stats(msgflow_name)

        print("Message Flow: " + msgflow_name + " of crit level " + str(msgflow_crit_level) + " Period " + str(msgflow_period))
        # Msgflow payload, currently A * msgpayload_size. Hopefully, real payload later
        # Let's say we create msgflow payload here
        msgflow_payload = "A" * msgflow_payload_size
        # Tuple for the thread
        args_tuple = [event, msgflow_name, msgflow_crit_level, msgflow_period, msgflow_payload]
        x = threading.Thread(target=write_data_uart, args=args_tuple)
        x.start()
        # Appending to list_threads for stopping them later
        list_threads.append(x)


def create_stats(msgflow_name):
    """ Function to create a entry in to the stats dict for MsgFlow Name with sent and recv. """
    sent_recv = {'sent': 0, 'recv': 0, 'error_na': 0}
    if msgflow_name not in stats.keys():
        stats[msgflow_name] = sent_recv

def error_message(msgflow_name):
    msgflow_name = msgflow_name.rstrip("\n")
    if '\n' in msgflow_name:
        msg_flows = msgflow_name.split("\n")
    else:
        msg_flows = []
        msg_flows.append(msgflow_name)

    # There might be a case where two ERROR message are sent simulantously in that case
    # message would contain 'ERROR:Kitchen Sensor\n:ML:26,ACK:Bathroom Sensor' So,
    # we remove :ML:
    for i in range(0, len(msg_flows)):
        if ":ML:" in msg_flows[i]:
            msg_flows[i] = msg_flows[i].split(",", 1)[1]

    for item in msg_flows:
        item_v = item.split(":")
        item_v = item_v[1]
        if item_v in stats.keys():
            stats[item_v]["error_na"] = stats[item_v]["error_na"] + 1



def ack_message(msgflow_name):
    """ Function to process the ACK message which is in the format ACK:Body Temperature """
    msgflow_name = msgflow_name.rstrip("\n")
    if '\n' in msgflow_name:
        msg_flows = msgflow_name.split("\n")
    else:
        msg_flows = []
        msg_flows.append(msgflow_name)

    # There might be a case where two ACK message are sent simulantously in that case
    # message would contain 'ACK:Kitchen Sensor\n:ML:26,ACK:Bathroom Sensor' So,
    # we remove :ML:
    for i in range(0, len(msg_flows)):
        if ":ML:" in msg_flows[i]:
            msg_flows[i] = msg_flows[i].split(",", 1)[1]

    for item in msg_flows:
        item_v = item.split(":")
        item_v = item_v[1]
        if item_v in stats.keys():
            stats[item_v]["recv"] = stats[item_v]["recv"] + 1


def write_data_uart(event, msgflow_name, msgflow_crit_level, msgflow_period, msgflow_payload):
    """ Writing data on the UART with msgflow_name, msgflow_crit_level, msgflow_payload """
    # Let's say we want to send two messages
    for i in range(0, 2):
#    while True:
        # Check for Global Variable if threads need to stop
        if event.isSet():
            break
        msg_uart = msgflow_name + "," + str(msgflow_crit_level) + "," + msgflow_payload + "\n"
        # Add the message into the message queue for writing into UART
        message_queues[s].put(msg_uart)
        print("Message written, sleeping")
        stats[msgflow_name]["sent"] = stats[msgflow_name]["sent"] + 1
        # Wait for the msgflow_period to send the next message
        event.wait(msgflow_period)

def connect_to_uart():
    """ Function to read UART and send messages on UART """
    # Run a while loop, with socket select, socket check when there's a message from UART
    # such as MFE allocations
    while True:

        # Wait for at least one of the sockets to be ready for processing
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for sock in readable:
            # Incoming message from UART
            if sock == s:
                data = read_socket(sock)
#                data = sock.recv(4096)
                print(data)
                if not data:
                    print('\nDisconnected from server')
                    sys.exit()
                else:
                    print(len(data))
                    if isinstance(data, str):
                        temp = data
                    else:
                        temp = data.decode('utf-8', errors='replace')
                        # buf = ""
                        # if '\n' in temp or '\r' in temp:
                        #     buf = buf + temp
                        #     buf.strip()
                        #     print(buf)
                        # else:
                        #     buf = buf + temp

                    # If Message Flow Allocation Message is received
                    # MFEA:[{'PS': 40, 'N': 'SigFox', 'MF': 'Energy Usage', 'PE': 3600, 'CL': 0}]
                    if temp.startswith('MFEA:') and temp.endswith("]"):
                        # Call the read_mfe function
                        temp2 = temp.split(":", 1)
                        read_mfe(temp2[1])

                    # If ACK of Message Flow sent message is received
                    # ACK:Energy Usage
                    if temp.startswith('ACK:'):
                        msgflow_name = temp
                        ack_message(msgflow_name)
                    # If STATS print the stats
                    if temp.startswith('STATS'):
                        print(stats)
                    if temp.startswith('ERROR:'):
                        msgflow_name = temp
                        error_message(msgflow_name)

        # Writing messages to UART
        for sock in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except:
                # No messages waiting so stop checking for writability.
    #            print("output queue for " + str(s.getpeername()) + " is empty")
                pass
    #            outputs.remove(s)
            else:
                # temp contains the original message
                temp = next_msg.split(",")
                # Splitting for printing
                print_msg = temp[0] + " " + temp[1]
                print("sending " + str(print_msg.rstrip()) + " to " + str(s.getpeername()))

                msg_len = len(next_msg)
                # 5 == 4 for :ML:
                len_of_header = 5 + len(str(msg_len))
                uart_msg = ":ML:" + str(msg_len + len_of_header) + "," + next_msg
                uart_msg = uart_msg.encode('utf-8')
                s.send(uart_msg)

if __name__ == '__main__':
    connect_to_uart()
