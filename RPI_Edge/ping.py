import time
import threading
import logging
from scapy.all import *

ROUTER = "192.168.1.254"
IOT = "192.168.1.219"
REMOTE = "8.8.8.8"

def ping_host(ip_addr):
    """Sends ICMP packets to IP, checks whether dead or alive and record time behind that"""
    time_host_alive = 0
    time_host_dead = 0

    # Creating the packet
    pkt = IP(dst=ip_addr)/ICMP()

    #Initial Check whether host is alive or dead
    ans = sr1(pkt, retry=0, timeout=1, verbose=False)
    if ans is None:
        print("Host " + str(ip_addr) + " is dead")
        return 1
    else:
        print("Host " + str(ip_addr) + " is alive")

    while True:
        time.sleep(0.5)
        ans = sr1(pkt, retry=0, timeout=1, verbose=False)

        # Host is dead and time_host_dead is not known
        if (ans is None and (time_host_dead == 0)):
            print("Host " + ip_addr + " is dead")
            time_host_dead = time.time()

        # Host came back online from being dead
        if (ans is not None and (time_host_dead != 0)):
            time_host_alive = time.time()
            time_taken = time_host_alive - time_host_dead
            print("Host "+ str(ip_addr) + " became dead at " + str(time_host_dead) + " and came back at " + str(time_host_alive) + " after " + str(time_taken) + " seconds.")
            break


def main():
#    ping_host("192.168.1.213")
    try:
# Ping IoT Device
        x = threading.Thread(target=ping_host, args=(IOT,))
        x.setDaemon(True)
        x.start()
# Ping router
        y = threading.Thread(target=ping_host, args=(ROUTER,))
        y.setDaemon(True)
        y.start()
# Ping Google
        z = threading.Thread(target=ping_host, args=(REMOTE,))
        z.setDaemon(True)
        z.start()
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print("\n! Received keyboard interrupt, quitting threads.\n")
        sys.exit()


if __name__ == "__main__":
    main()
