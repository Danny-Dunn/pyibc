import http.client
import json

bc2_objects = {
    "network":      34,
    "status":       19,
    "modelinfo":    11,
    "loads":        13,
    "load":         32,
    "multi-config": 17,
    "load-extended":  16
}

class boiler:
    ip_addr = ""
    boiler_no = 0

    def __init__(self, ip_addr, boiler_no = 0):
        self.ip_addr = ip_addr
        self.boiler_no = boiler_no
        self.conn = http.client.HTTPConnection(ip_addr)

    def get_object(self, objectid):
        query = {
            "object_no": 100,
            "object_request": bc2_objects[objectid],
            "boiler_no": self.boiler_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + json.dumps(query))
        response = self.conn.getresponse()
        print(response.reason)
        print(response.status)
        return json.loads(response.read())

    def get_load(self, load_no):
        query = {
            "object_no": 100,
            "object_request": bc2_objects["load"],
            "boiler_no": self.boiler_no,
            "load_no": load_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + json.dumps(query))
        response = self.conn.getresponse()
        print(response.reason)
        print(response.status)
    
    def get_load_extended(self, load_no):
        query = {
            "object_no": 100,
            "object_request": bc2_objects["load-extended"],
            "boiler_no": self.boiler_no,
            "object_index": load_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + json.dumps(query))
        response = self.conn.getresponse()
        print(response.reason)
        print(response.status)

    def get_num_loads(self):
        loads = self.get_object("loads")
        numloads = 0
        for i in range(1,5):
            if loads["Load" + i + "Type"] != 0:
                numloads += 1

    def check_connection(self):
        self.get_object("network")
