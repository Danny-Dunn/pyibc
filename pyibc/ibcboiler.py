import http.client
import json
import urllib

bc2_objects = {
    "network":      34,
    "sensors":      20,
    "status":       19,
    "modelinfo":    11,
    "loads":        13,
    "load":         32,
    "multi-config": 17,
    "load-extended":  16
}

class LoadStatus:
    __init__():
        inletTemp = 0.0
        outletTemp = 0.0
        targetTemp = 0.0
        firingRate = 0.0 #kW
        isFiring = False

class BoilerStatus:
    __init__():
        isFiring = False
        firingRate = 0.0 #kW
        loads = [
            LoadStatus(),
            LoadStatus(),
            LoadStatus(),
            LoadStatus(),
        ]




class boiler:
    ip_addr = ""
    boiler_no = 0
    num_loads = 0



    def __init__(self, ip_addr, boiler_no = 0):
        self.ip_addr = ip_addr
        self.boiler_no = boiler_no
        self.conn = http.client.HTTPConnection(ip_addr)
        num_loads = self.get_num_loads()

    def celsius_from_raw(raw):
        return raw/4

    def query_object(self, objectid):
        query = {
            "object_no": 100,
            "object_request": bc2_objects[objectid],
            "boiler_no": self.boiler_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + urllib.parse.quote_plus(json.dumps(query)), headers = {"cookie" : "MetricMode=0; TECH_AUTHORIZED=103"})
        response = self.conn.getresponse()
        print(urllib.parse.quote_plus("/cgi-bin/bc2-cgi?json=" + json.dumps(query)))
        print(response.reason)
        print(response.status)
        return json.loads(response.read())

    def query_load(self, load_no):
        query = {
            "object_no": 100,
            "object_request": bc2_objects["load"],
            "boiler_no": self.boiler_no,
            "load_no": load_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + json.dumps(query))
        response = self.conn.getresponse()
        
    
    def query_load_extended(self, load_no):
        query = {
            "object_no": 100,
            "object_request": bc2_objects["load-extended"],
            "boiler_no": self.boiler_no,
            "object_index": load_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + json.dumps(query))
        response = self.conn.getresponse()
        if response.status != 200:
            return 

    

    def get_num_loads(self):
        loads = self.query_object("loads")
        numloads = 0
        for i in range(1,5):
            if loads["Load" + str(i) + "Type"] != 0:
                numloads += 1
        return numloads

    def check_connection(self):
        self.query_object("network")
