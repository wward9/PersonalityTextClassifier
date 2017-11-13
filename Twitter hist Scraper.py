# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 23:59:00 2017

@author: Ureridu
"""

from stem import Signal
from stem.control import Controller
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
import time
from random import randint

'''
download and install tor.
Add the below into your torrc file.  Mine was located here: C:\~blaghblagh~\Tor Browser\Browser\TorBrowser\Data\Tor
    ControlPort 9051
    HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE
    
    
Also, tor does need to be running in the background.  Will make it open on initiation later. if i feel like it....


looks like new ip requests need to be staggered, or else the same ip is given

'''


def init_torified_bowser():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE')
        controller.signal(Signal.NEWNYM)

    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9150)
    profile.set_preference("javascript.enabled", False)

    bowser = webdriver.Firefox(profile)
#    bowser.get('https://httpbin.org/ip')
#    time.sleep(5)
#    bowser.close()
    return bowser


def multi_threader(funk, site_list):
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(funk, site_list, timeout=15)


def scraper(site):
#    print('scrapey scrapey')
#    print(site)
    time.sleep(randint(5,60))
    bowser = init_torified_bowser()
    bowser.get(site)
    time.sleep(5)
    #bowser.close()


site_list = ["https://httpbin.org/ip" for i in range(4)]

multi_threader(scraper, site_list)
#init_torified_bowser()