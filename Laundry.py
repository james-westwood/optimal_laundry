#!/usr/bin/env python
# coding: utf-8

# In[177]:


import json
import requests
import time
import datetime
from collections import namedtuple
from datetime import timedelta



key = "cb7aeb04a283a1aa9497979348788156"
check_interval = 2 # 1800
limit = 5 # 18
ip_key = "6523a6731157c2f993c60800f9fdfcfb"
ip_base_url = "http://api.ipstack.com/{}?access_key={}"
ip_add = "62.130.190.255"

def geo_locate(ip_base_url,ip_key,ip_add): #this gets location data using an ip address via an API lookup at ipstack.com
    url = ip_base_url.format(ip_add,ip_key)
    data = requests.get(url)
    return (data)

location_data =(geo_locate(ip_base_url,ip_key,ip_add).json())

def get_lat_lon(location_data): #This gets the lat and long coords from the geo_locate data json
    loca = namedtuple('loca','lat lon')
    loca = loca(location_data['latitude'],location_data['longitude'])
    return loca

# print (location_data)

def get_city_country(location_data):
    loca = namedtuple('loca','city country')
    loca = loca(location_data['city'],location_data['country_name'])
    return loca


# # print(location_data.json())

# # print(type(loca))

# print(get_city_country(location_data))


## Acceptable Weather conditions
# # 801 = Clouds (few clouds: 11-25%)
# # 802 = Clouds (scattered clouds: 25-50%)
# # 800 = Clear (clear sky)
##  803 = broken clouds: 51-84% 
acceptable_conditions = namedtuple('acceptable_conditions','few_clouds scatt_clouds clear broken_clouds' )
acceptable_conditions=acceptable_conditions(801,802,800,803) #codes stored as int

def is_sunny(data):
    # weather = ("Sunny", "Sunny")
    weather = weather_parse(data) 
    weather_code= weather_code_parse(data)
#     if ((weather[0] and weather[1]) == ("Clear") or (weather[0] and weather[1]) == ("Sunny")):
    if any(cond == weather_code[0] for cond in acceptable_conditions) and any(cond == weather_code[1] for cond in acceptable_conditions):
            return True
    else:
        return False
def api(location,key):
    response = requests.get("http://api.openweathermap.org/data/2.5/forecast?" + location + "&APPID=" + key)
    # check if fails
    data = json.loads(response.content)
    return data
def weather_parse(data): # This extracts the main weather condition (descriptive word, e.g. "Clouds") from returned weather data
    start = data['list'][0]['weather'][0]['main']
    end = data['list'][1]['weather'][0]['main']
    return (start,end)

def weather_code_parse(data): # This extracts the main weather condition (ID or code number) from returned weather data
    start_id = data['list'][0]['weather'][0]['id']
    end_id = data['list'][1]['weather'][0]['id']
    return (start_id,end_id)

def daytime(data):
    sunrise = data['city']['sunrise']
    sunset = data['city']['sunset']
    now= int(time.time()) #getting current time to nearest second
    now_plus_3=now+10800 #adding 3 hours worth of seconds
    if (sunrise < now < now_plus_3 <sunset): #checks if it is after sunrise and will be daylight hours for the next 3 hours
        return True
    return False


def checking_msg(location_city, location_country):
    return "Checking weather conditions for optimal laundry drying in {}, {}".format(location_city, location_country)

def weather_now_later(weather_now,now_code,weather_later,later_code):
    return "Weather now: {} (code: {})\nForecast for 3 hours time: {} (code: {})\n".format(weather_now,now_code,weather_later,later_code)

# weather_parse(data)[0],weather_code_parse(data)[0],weather_parse(data)[1],weather_code_parse(data)[0]





# # #Location related stuff
location_data =(geo_locate(ip_base_url,ip_key,ip_add)).json()
loca = get_lat_lon(location_data)
city_country = get_city_country(location_data)
location_city= city_country.city #using the named tuple named element "city"
location_country = city_country.country #using the named tuple named element "country"
location = "lat={}&lon={}".format(loca.lat,loca.lon)
# location = "lat=41.390205&lon=2.154007" #this is the lat/lon of Barcelona....needed to test for sunny conditions
data = api(location,key)



# # main function
i = 0
while (is_sunny(data) != True and i < limit): #if is_sunny(data) returns True, this means the weather conditions are acceptable
    weather_now=weather_parse(data)[0]
    now_code=weather_code_parse(data)[0]
    weather_later=weather_parse(data)[1]
    later_code=weather_code_parse(data)[0]
    print(weather_now_later(weather_now,now_code,weather_later,later_code),"\nDon't waste time hanging laundry in sub-optimal conditions")
    if daytime(data) == False: # I put this inside the while loop because after waiting for 3 hours we will want to check that there's still enough daylight left
        print("Not enough daylight. Wait until tomorrow") 
    else:
        print("There are {} enough daylight hours. ".format("still" if i>0 else ""), end="") # statement conditional formatting 
        print(checking_msg(location_city, location_country))
    time.sleep(check_interval) #this would usually be 3 hours between checks
    i += 1
    data = api(location,key) # data needs to be re-checked after a 3 hours wait
else:
    if (i < limit):
        print(checking_msg(location_city, location_country))
        print(weather_now_later())
        print("Hang out washing")
        time.sleep(3) #this would be 3 hours
        print("It's been 3 hours! Your washing should be dry")
    else:
        print("Completed {} checks. No washing today :(".format(limit))


# In[ ]:




