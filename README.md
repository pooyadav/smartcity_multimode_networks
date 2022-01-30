# smartcity_multimode_networks

SmartCity: Data negotiability in multi-mode communication networks
This project is subawarded by Human Data Interaction: Legibility, Agency, Negotiability, is a ‘network plus’ project funded by the UK Engineering and Physical Sciences Research Council (EPSRC). The HDI network runs from July 2018 to June 2021 (EP/R045178/1), more details here: https://hdi-network.org/, and https://poonamyadav.net/hdi


# Team

PI - Dr Poonam Yadav (PI), University of York, UK

Collaborators and Interns

 - Mr Angelo Feraudo (University of Bologna, Italy)

 - Mr Vijay Kumar (University of Bristol, UK)



Timeline: January - November 2021



# Project Overview

As the concept of the smart city is growing from abstract ideas and a lab environment to real deployments, many intelligent sensor-based IoT applications are emerging. Some of these applications use a camera or audio-based sensors in public spaces such as streets, parks, train stations, public squares and stadiums. Many of these deployments are used for a specific purpose and dedicated infrastructure is setup for the applications, for example, City council CCTV (close circuit television) installed in streets and public spaces for security surveillance. Similarly, the InLinkUK free wifi kiosk​s in public spaces installed by BT provides dedicated free internet service with the partnership of an advertising company. All these examples are independent solutions in the public space. If these resources and infrastructure could be shared, this will create new services and better co-created smart cities and speed up the deployment of new services in an economical way. In order to deploy many of these smart sensor-based applications using shared infrastructure and resources, a well-structured data negotiation framework is required which complies with GDPR data regulations as well as citizen’s privacy in public places. To understand this further, we need to investigate the following questions for building the data legibility and negotiability framework:

Q1: Who supports the necessary public IoT infrastructure, and why?
Q2: Who will benefit from this infrastructure and what are the ethical, cultural, social, technical and economic barriers in achieving full benefit?
Q3: Who has access to the public space citizen data and how this data is going to be used?
Q4: What current mechanisms are used to take data usage consent from an end-user and how they are informed by other service users and providers that are involved in the whole ecosystem?


# Publications:
-> Vijay Kumar, Poonam Yadav and  Leandro Soares Indrusiak: Building IoT Resilient Edge using LPWAN and WiFi, IMC, 2021 ([PDF](https://conferences.sigcomm.org/imc/2021/pdf/Building%20IoT%20Resilient%20Edge%20using%20LPWAN%20and.pdf))

-> A. Feraudo, P. Yadav, V. Safronov, D. A. Popescu, R. Mortier, S. Wang, P. Bellavista, and J. Crowcroft:
   Colearn: Enabling federated learning in mud compliant iot edge networks. The 3rd International Workshop on Edge Systems, Analytics and Networking (EdgeSys20).   New York: ACM, April 2020 ([PDF](https://poonamyadav.net/Papers/EdgeSys2020.pdf))
   

---------------------------------------------------------------------------------------------------------------------



The FiPY generates the MFEA (Message Flow Element Allocation) message (a list of dict)

```json
"[{'PS': 40, 'N': 'LoRaWAN', 'PE': 3600, 'MF': 'Energy Usage', 'CL': 0}, {'PS': 30, 'N': 'LoRaWAN', 'PE': 30, 'MF': 'Body Temperature', 'CL': 0}, {'PS': 40000, 'N': 'LoRaWAN', 'PE': 10, 'MF': 'Front Door Sensor', 'CL': 0}, {'PS': 40000, 'N': 'Wi-Fi', 'PE': 10, 'MF': 'Kitchen Sensor', 'CL': 0}, {'PS': 80, 'N': 'LoRaWAN', 'PE': 10, 'MF': 'Bathroom Sensor', 'CL': 0}, {'PS': 40000, 'N': 'Wi-Fi', 'PE': 10, 'MF': 'Bedroom Sensor', 'CL': 0}, {'PS': 1000, 'N': 'LoRaWAN', 'PE': 10, 'MF': 'Fall Detection', 'CL': 0}, {'PS': 1000, 'N': 'LoRaWAN', 'PE': 5, 'MF': 'Heart Monitoring', 'CL': 0}]"
```

A sample dict is

```
{'PS': 40, 'N': 'LoRaWAN', 'PE': 3600, 'MF': 'Energy Usage', 'CL': 0}
```
where

- PS is Payload Size, 
- N is the Network, 
- PE is Period, 
- MF is Message Flow and 
- CL is Criticality Level.

We add a header `MFEA:` to the message and send it to UART for RPI to read

```
"MFEA:[{'PS': 40, 'N': 'LoRaWAN', 'PE': 3600, 'MF': 'Energy Usage', 'CL': 0}, {'PS': 30, 'N': 'LoRaWAN', 'PE': 30, 'MF': 'Body Temperature', 'CL': 0}, {'PS': 40000, 'N': 'LoRaWAN', 'PE': 10, 'MF': 'Front Door Sensor', 'CL': 0}, {'PS': 40000, 'N': 'Wi-Fi', 'PE': 10, 'MF': 'Kitchen Sensor', 'CL': 0}, {'PS': 80, 'N': 'LoRaWAN', 'PE': 10, 'MF': 'Bathroom Sensor', 'CL': 0}, {'PS': 40000, 'N': 'Wi-Fi', 'PE': 10, 'MF': 'Bedroom Sensor', 'CL': 0}, {'PS': 1000, 'N': 'LoRaWAN', 'PE': 10, 'MF': 'Fall Detection', 'CL': 0}, {'PS': 1000, 'N': 'LoRaWAN', 'PE': 5, 'MF': 'Heart Monitoring', 'CL': 0}]"
```

The [RPI Script](https://github.com/bitvijays/smartcity_multimode_networks/blob/algo-implementation-FiPy/RPI_Edge/cpu_temp_uart.py) reads the above message, take out each dict

```
{'PS': 40, 'N': 'LoRaWAN', 'PE': 3600, 'MF': 'Energy Usage', 'CL': 0}
```

and creates a thread to send the a message of size PS on the UART, sleeps for PE time.

Sample message on UART by a thread is in the format
```
"Message Flow Name, Criticality Level, Payload"
```
A example 
```
{"Energy Usage", 0, EnergyUsageEnergyUsage
```

FiPy on receiving the message, checks whether the Message Flow with the Criticality level has been allocated.

If not, it will send a error message to the RPI
```
"ERROR:Bedroom Sensor:NOT_ALLOCATED"
```

If it has been allocated, it will check whether the allocated network interface is connected and then send the message via that interface.

If any error is received, it will send 
```
"ERROR:Bedroom Sensor:NOT_DELIVERED"
```
If no error has been received, it will send
```
ACK:Energy Usage
```

The RPI creates a stats dictionary to store how many messages has been sent, ack received etc.
```
{'Energy Usage': {'sent': 1, 'recv': 1, 'error_na': 0}, 'Body Temperature': {'sent': 2, 'recv': 2, 'error_na': 0}, 'Front Door Sensor': {'sent': 2, 'recv': 2, 'error_na': 0}, 'Kitchen Sensor': {'sent': 2, 'recv': 2, 'error_na': 0}, 'Bathroom Sensor': {'sent': 2, 'recv': 2, 'error_na': 0}, 'Bedroom Sensor': {'sent': 2, 'recv': 2, 'error_na': 0}, 'Fall Detection': {'sent': 2, 'recv': 2, 'error_na': 0}, 'Heart Monitoring': {'sent': 2, 'recv': 2, 'error_na': 0}}
```

On the cloud, the cloud gets the data via HTTP POST, Lora/ Sigfox callbacks and store it into a file.
