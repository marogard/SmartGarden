import requests
import time
import adafruit_dht
import logging
from datetime import datetime
from board import *

#Logging library not working here, cannot be installed / gives errors.
#log = logging.getLogger("my-logger")
#logging.basicConfig(filename=/home/pi/Dokumente/Logs/RadiatorLog.log, encoding='utf-8',level=logging.DEBUG)
#log.info("Hello, world")

#Sensor Pin for readout of Data from DHT22 sensor
SENSOR_PIN = D4
#define sensor name from NEW (broken) adafruit_dht library
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
#define temp & hum variables (not used anymore since getTemperature() function exists.
#temperature = dht22.temperature
#humidity = dht22.humidity
#define payload options for url conversion with requests library
#"on" turns on, "off" turns off, "toggle" switches between states and "status" returns status
payload_on = {"user": "admin", "password": "KahlanAmnell!1", "cmnd": "Power ON"}
payload_off = {"user": "admin", "password": "KahlanAmnell!1", "cmnd": "Power OFF"}
payload_toggle = {"user": "admin", "password": "KahlanAmnell!1", "cmnd": "Power TOGGLE"}
payload_status = {"user": "admin", "password": "KahlanAmnell!1", "cmnd": "Power"}

#Timestamps for log and printing
time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

#Temperature & humidity request retry functions THANKS TO MAXIMILIAN P.
def getTemperature(countTries=5):
    for x in range(0, countTries):
        try:
            return dht22.temperature;
        except RuntimeError:
            print("Failed to retrieve temperature. Trying again.")
    return 0

def getHumidity(countTries=5):   
    for x in range(0, countTries):
        try:
            humidity = dht22.humidity
            return humidity;
        except RuntimeError:
            print("Failed to retrieve humidity. Trying again.")
    return 0

#Logging function to specified file
def log(text):
    f = open("/home/pi/Dokumente/Logs/RadiatorLog.txt", "a")
    f.write(time_formatted + ": " + text)
    f.close()
    print(time_formatted + ": " + text)


#Target temperature & humidity variables
targetTempUpperBound = 23
targetTempLowerBound = 21
targetHum = 60


#Testing loop for turning socket on and off
#while True:
#    r=requests.get("http://192.168.0.87/cm", params= payload_on)
#    print(r.text)
#    time.sleep(15)
#    r=requests.get("http://192.168.0.87/cm", params=payload_off)
#    print(r.text)
#    time.sleep(15)

#Nicely formated values of hum & temp readout
#print(f"Humidity= {humidity:.2f}%")
#print(f"Temperature= {temperature:.2f}°C")

temperature = getTemperature()
humidity = getHumidity()
logging.info("Starting humidity is "+ str(humidity) + "%, temperature is " + str(temperature) + "°C.")


#Now actual loop for temperature management
while True:
    r=requests.get("http://192.168.0.87/cm", params= payload_status)
    temperature = getTemperature()
    if float(temperature) < float(targetTempLowerBound) and "OFF" in r.text :
        r=requests.get("http://192.168.0.87/cm", params= payload_on)
        log("Beginning heating sequence.")
        time.sleep(20)
    else:
        if float(temperature) < float(targetTempUpperBound):
            log(str(temperature) + "°C, still heating up to " + str(targetTempUpperBound) + "°C, power is on.")
            time.sleep(30)
        else:
            r=requests.get("http://192.168.0.87/cm", params= payload_off)
            log("Target temperature of " + str(targetTempUpperBound) + "°C exceeded, current temperature is " + str(temperature) +"°C, shutting down.")
            r=requests.get("http://192.168.0.87/cm", params= payload_status)
            if "OFF" in r.text:
                log("Shutdown successful, timing out for 10 minutes.")
                time.sleep(600)
            else:
                r=requests.get("http://192.168.0.87/cm", params= payload_off)
                time.sleep(5)
                r=requests.get("http://192.168.0.87/cm", params= payload_status)
                if "OFF" in r.text:
                    log("Shutdown successful, timing out for 10 minutes.")
                    time.sleep(600)
                else:
                    log("Problem with shutdown, please disconnect manually. Automatic retry in 20 seconds.")
                    time.sleep(20)
            
