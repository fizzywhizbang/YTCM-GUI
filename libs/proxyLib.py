# YTCM - Youtube Channel Monitor
# Copyright (C) 2019  Marc Levine
#
# This file is part of YTCM.
#
# YTCM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YTCM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YTCM.  If not, see <http://www.gnu.org/licenses/>.

import requests
try:
    from StringIO import BytesIO
except ImportError:
    from io import BytesIO
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
from time import sleep

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]


def getProxyList():
    # Retrieve latest proxies
    url = 'https://www.sslproxies.org/'
    header = {'User-Agent': str(ua.random)}
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'lxml')
    proxies_table = soup.find(id='proxylisttable')

    # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })

    return proxies

def getProxyList2(proxies):
    # Retrieve latest proxies
    try:
        url = 'https://free-proxy-list.net'
        header = {'User-Agent': str(ua.random)}
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.text, 'lxml')
        proxies_table = soup.find("table", {"class": "bg"})
        #print(proxies_table)
        # Save proxies in the array
        for row in proxies_table.find_all("tr", {"class": "cells"}):
            google = row.find_all('td')[5].string
            if google == "yes":
                #print(row.find_all('td')[1].string)
                proxies.append({
                    'ip': row.find_all('td')[1].string,
                    'port': row.find_all('td')[2].string
                })
    except:
        print("broken")
    # Choose a random proxy
    try:
        url = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
        header = {'User-Agent': str(ua.random)}
        response = requests.get(url, headers=header)
        textArray = response.text.splitlines()
        
        for row in textArray:
            items = row.split(":")
            
            proxies.append({
                'ip': items[0],
                'port': items[1]
            })
    except:
        print("broken")

    return proxies

def getProxy():
    proxies = getProxyList()
    proxies = getProxyList2(proxies)
    proxy = random.choice(proxies)
    proxyformat = proxy["ip"] + ":" + proxy["port"]
    return proxyformat


