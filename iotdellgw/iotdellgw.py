import serial
import pynmea2
import re
from math import radians, cos, sin, asin, sqrt
import requests
import json

"""

THIS CODE IS NOT PRODUCTION READY AND NO RESPONSIBILITY FOR IT's ACCURATENESS IS  IMPLIED. 
IT SHOULD ONLY BE USED TO VERIFY CONNECTIVITY TO THE ONBOARD GPS SERIAL AND CONNECTIVITY 
TO THE DAVRA PLATFORM TENANT USING THE CODE.
"""
remoteServer = 'http://advisoryme.connecthing.io'
remoteServerPort = '80'
deviceId = 'DELL123456'

serialPort="/dev/ttyS5"

conn = serial.Serial(
            port=serialPort,
            baudrate=9600,
            stopbits=serial.STOPBITS_ONE
        )

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def putMetric(data):
        try:
                url = remoteServer + '/api/v1/iotdata'
                headers = { 'content-type': 'application/json' }
                response = requests.put(url, data=json.dumps(data), headers=headers, verify=False)
                #print(response)
        except Exception as ex:
                print("Failed to PUT data to remote server")

data = conn.read(conn.inWaiting())
previousLat = 0
previousLong = 0
count=0
while True:
        data = conn.read(conn.inWaiting())
        if len(data) > 2:
                latlong = data.split('GNGLL')[1]
                data = data.replace('\n','')
                data = data.replace('\r','')
                msg = pynmea2.parse('$GNGLL' + latlong)
                speed = haversine(previousLat, previousLong, msg.latitude, msg.longitude)
                #print("%.2f" % speed)
                lat = msg.latitude
                long = msg.longitude
                metric = {}
                metric['UUID'] = deviceId
                metric['name'] = '4358_107'
                metric['value'] = round(speed, 2)
                metric['latitude'] = lat
                metric['longitude'] = long
                metric['msg_type'] = 'datum'
                putMetric(metric)
                previousLat = msg.latitude
                previousLong = msg.longitude
                count = count +1