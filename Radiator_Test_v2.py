import requests
import time
import adafruit_dht
from board import *

#Sensor Pin for readout of Data from DHT22 sensor
SENSOR_PIN = D4
#define sensor name from NEW (broken) adafruit_dht library
dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
#define temp & hum variables
temperature = dht22.temperature
humidity = dht22.humidity
#define payload options for url conversion with requests library
#"on" turns on, "off" turns off, "toggle" switches between states and "status" returns status
payload_on = {"user": "admin", "password": "xxx", "cmnd": "Power ON"}
payload_off = {"user": "admin", "password": "xxx", "cmnd": "Power OFF"}
payload_toggle = {"user": "admin", "password": "xxx", "cmnd": "Power TOGGLE"}
payload_status = {"user": "admin", "password": "xxx", "cmnd": "Power"}

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

print(humidity, temperature)

#Following two lines are only for testing purposes
#r=requests.get("http://192.168.0.87/cm", params= payload_status)
#print(r.text)

#Now actual loop for temperature management
while True:
    r=requests.get("http://192.168.0.87/cm", params= payload_status)
    #Here is where i need a retry option due to a failure to retrieve sensor data that happens regularly
    temperature = dht22.temperature
    humidity = dht22.humidity
    if temperature < 22 and "OFF" in r.text :
        r=requests.get("http://192.168.0.87/cm", params= payload_on)
        print("Beginning heating sequence")
        time.sleep(20)
    else:
        if temperature < 24:
            print(temperature + ", still heating, power is on")
            time.sleep(30)
        else:
            r=requests.get("http://192.168.0.87/cm", params= payload_off)
            print("Target temperature of " + temperature + " degrees Celsius reached, shutting down")
            r=requests.get("http://192.168.0.87/cm", params= payload_status)
            if "OFF" in r.text:
                print("Shutdown successful, timing out for 10 minutes")
            else:
                r=requests.get("http://192.168.0.87/cm", params= payload_off)
                time.sleep(5)
                r=requests.get("http://192.168.0.87/cm", params= payload_status)
                if "OFF" in r.text:
                    print("Shutdown successful, timing out for 10 minutes")
                    time.sleep(600)
                else:
                    print("Problem with shutdown, please disconnect manually. Automatic retry in 20 seconds.")
                    time.sleep(20)
            
