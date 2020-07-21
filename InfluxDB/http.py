#!/usr/bin/env python

from influxdb import InfluxDBClient
import tornado.ioloop
import tornado.web
import pprint
import json

client = InfluxDBClient(host='localhost', port=8086, database='example')
client.create_database('example')

class MyDumpHandler(tornado.web.RequestHandler):
    def post(self):
        pprint.pprint(self.request)
        pprint.pprint(self.request.body)
        if self.request.uri == "/wifi":
            data = self.request.body
            temp_epoch = data.split(':')[0]
            temp_cputemp = data.split(':')[1]
	    medium = "wifi"
            time = int(temp_epoch)
            temp = float(temp_cputemp)
        elif self.request.uri == "/sigfox":
            medium = "sigfox"
            sigfox_json = json.loads(self.request.body)
            sigfox_data = sigfox_json["data"]
            print(sigfox_data)
            data = sigfox_data.decode('hex')
            print(data)
            # Converting the data from 
            # Assuming data was like epochtime:cputime like 1594329236:66.705 which is 17 bytes.
            # Adding last two digit of epochtime (add it with 00 at the server and removing : and . we make it to 12 bytes)
            # Reduced to 1594329236:66.705 to 159432926670
            # First 8 digit of time
            time = data[0:8]
            # Last 4 digit of temp
            temp_cpu = data[-4:]
            # Added 00 to convert back to epoch time
            time = time + "00"
            time = int(time)
            # Added . and converted to float
            temp_cpu1 = temp_cpu[:-2] + "." + temp_cpu[-2:]
            temp = float(temp_cpu1)

        data2 = convert_data_influxdb(time, temp, medium)
        insert_influxdb(data2)


def insert_influxdb(data):

    # For every message received, insert the data to the InfluxDB database
    # We assume that the data received is in the InfluxDB format of tags, fields, time etc.
    client.write_points(data, time_precision="s")
    print("Data written")

def convert_data_influxdb(time, temp, medium):
    """Function to convert SCK data to InfluxDB data format time, fields, tags, measurement"""

# Getting Tags in to Dict
    tags_dict = {}
    fields_dict = {}

    key_value = {"temp": temp}
    fields_dict.update(key_value)
    key_value = {"medium": medium}
    fields_dict.update(key_value)

    data2 = [
         {
             "measurement" : 'PyMaker',
             "time" : time,
             "tags" : tags_dict,
             "fields": fields_dict
         }
    ]

    return data2


if __name__ == "__main__":
    tornado.web.Application([(r"/.*", MyDumpHandler),]).listen(8080)
    tornado.ioloop.IOLoop.instance().start()
