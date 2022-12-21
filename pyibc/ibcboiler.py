import http.client
import json
import urllib

bc2_objects = {
    "network":      34,
    "fan":      20,
    "status":       19,
    "modelinfo":    11,
    "loads":        13,
    "load":         32,
    "multi-config": 17,
    "load-extended":  16
}

class LoadStatus:
    def __init__(self):
        self.returnTemp = 0.0
        self.supplyTemp = 0.0
        self.targetTemp = 0.0
        self.tankTemp = -1.0 #tank temp is negative for no tank
        self.firingRate = 0.0 #kW
        self.isFiring = False

class FanStatus:
    def __init__(self):
        self.currentSpeed = 0.0 #RPM
        self.targetSpeed = 0.0
        self.dutycycle = 0.0 # 0-1
        self.requiredPressure = 0.0
        self.currentPressure = 0.0
        self.ventFactor = 0.0
        self.heatOut = 0.0
        self.inletTemp = 0.0
        self.inletPressure = 0.0
        self.outletTemp = 0.0
        self.flowRate = 0.0

        

class BoilerStatus:
    def __init__(self, numLoads):
        self.isFiring = False
        self.firingRate = 0.0 #kW
        self.numLoads = numLoads
        self.loads = [
            LoadStatus(),
            LoadStatus(),
            LoadStatus(),
            LoadStatus(),
        ]
        self.boardTemp = 0.0
        self.outdoorTemp = 0.0
        self.indoorTemp = 0.0
        self.tankTemp = 0.0
        self.returnTemp = 0.0
        self.supplyTemp = 0.0
        self.pumps = 0
        self.servicing = 0
        self.status = ""
        self.warnings = ""
        self.fan = FanStatus()
        self.inletPressure = 0.0 #PSI

        


class boiler:
    ip_addr = ""
    boiler_no = 0
    num_loads = 0

    def __init__(self, ip_addr, boiler_no = 0):
        self.ip_addr = ip_addr
        self.boiler_no = boiler_no
        self.conn = http.client.HTTPConnection(ip_addr)
        self.status = BoilerStatus(self.get_num_loads())

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

    #these functions are rather unimportant and dont really give much useful info

    def query_load(self, load_no):
        query = {
            "object_no": 100,
            "object_request": bc2_objects["load"],
            "boiler_no": self.boiler_no,
            "load_no": load_no
        }
        self.conn.request("GET", "/cgi-bin/bc2-cgi?json=" + json.dumps(query))
        response = self.conn.getresponse()

        unmarshalled = json.loads(response.read())

        self.status.loads[load_no].returnTemp = unmarshalled["ReturnT"]
        self.status.loads[load_no].supplyTemp = unmarshalled["SupplyT"]

        
    
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

    def query_fan(self):
        resp = self.query_object("fan")
        
        #TODO error handling
        if(resp == -1):
            return

        self.status.fan.currentSpeed = resp["FanSpeed"]
        self.status.fan.targetSpeed = resp["FanTarget"]
        self.status.fan.dutycycle = resp["FanDuty"]
        self.status.fan.currentPressure = resp["FanP"]
        self.status.fan.requiredPressure = resp["RequiredP"]
        self.status.fan.ventFactor = resp["VentFactor"]
        self.status.fan.heatOut = resp["HeatOut"]
        self.status.fan.flowRate = resp["FlowRate"]

        self.status.isFiring = resp["Firing"] > 0

    def query_status(self):
        resp = self.query_object("status")
        
        #TODO error handling
        if(resp == -1):
            return

        self.status.status = resp["Status"]
        self.status.warnings = resp["Warnings"]
        self.status.firingRate = resp["MBH"]
        self.status.outdoorTemp = self.celsius_from_raw(resp["OutdoorT"])
        self.status.indoorTemp = self.celsius_from_raw(resp["IndoorT"])
        self.status.tankTemp = self.celsius_from_raw(resp["TankT"])
        self.status.pumps = resp["Pumps"]
        self.status.servicing = resp["Servicing"]
        self.status.inletPressure = resp["InletPressure"]

    def query_all(self):
        self.query_status()
        self.query_fan()


    def get_num_loads(self):
        loads = self.query_object("loads")
        numloads = 0
        for i in range(1,5):
            if loads["Load" + str(i) + "Type"] != 0:
                numloads += 1
        return numloads

    def check_connection(self):
        self.query_object("network")
