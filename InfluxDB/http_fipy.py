#!/usr/bin/env python

from influxdb import InfluxDBClient
import tornado.ioloop
import tornado.web
import pprint
import json
import base64

#file1 = open("MyFile.txt","a") 

class MyDumpHandler(tornado.web.RequestHandler):
    def post(self):
        pprint.pprint(self.request)
#        pprint.pprint(self.request.body)
#        print(self.request.body)
        print(self.request)
        if self.request.uri == "/wifi":
            data = self.request.body
            data2 = "Wi-Fi:" + data + "\n"
        if self.request.uri == "/sigfox":
            data = self.request.body
            data2 = json.loads(data)
            payload_hex = data2["data"]
            payload = payload_hex.decode('hex')
            data2 = "SigFox:" + payload + "\n"
        if self.request.uri == "/lora":
            data = self.request.body
            data2 = json.loads(data)
            payload_base64 = data2["payload_raw"]
            payload = base64.b64decode(payload_base64)
            data2 = "LoRa:" + payload + "\n"
        file1 = open("MyFile.txt","a") 
        file1.write(data2)
        file1.close()






if __name__ == "__main__":
    tornado.web.Application([(r"/.*", MyDumpHandler),]).listen(8080)
    tornado.ioloop.IOLoop.instance().start()
