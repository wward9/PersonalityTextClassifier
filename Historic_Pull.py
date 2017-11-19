# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 23:59:00 2017

@author: Ureridu
"""

from stem import Signal
from stem.control import Controller
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from random import randint
import pandas

'''
download and install tor.
Add the below into your torrc file.  Mine was located here: C:\~blaghblagh~\Tor Browser\Browser\TorBrowser\Data\Tor
    ControlPort 9051
    HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE


Also, tor does need to be running in the background.  Will make it open on initiation later. if i feel like it....


looks like new ip requests need to be staggered, or else the same ip is given

'''


def roxeanne():
    global red_light
    while 1:
        time.sleep(1)
        if red_light:
            out = red_light.pop(0)
            time.sleep(9)

            if out == 'done':
                print('finished')
                break


def init_torified_bowser():
    look = 1
    c = 0
    while look:
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password = '16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE')
                controller.signal(Signal.NEWNYM)

            look = 0

        except Exception as e:
            print(e)
            c += 1
            time.sleep(5)
            if c <= 5:
                look = 1
                print('failed')

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


def multi_threader(funk, site_list, workers):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = executor.map(funk, site_list, timeout=15)
        return futures


def scraper(site):
    try:
        global red_light
        ident = threading.get_ident()

        while ident not in red_light:
            red_light.append(ident)
            time.sleep(1)

        while ident in red_light:
            time.sleep(1)

        print(ident)

        bowser = init_torified_bowser()
        bowser.get(site)
        time.sleep(1)
        bowser.close()

    except Exception as e:
        print(e)
        
    return 1


def init_scraper():
    site_list = ["https://httpbin.org/ip" for i in range(12)]
    futures = multi_threader(scraper, site_list, 4)
    red_light.append('done')

    for i, f in enumerate(futures):
        if i == 0:
            output = pandas.DataFrame(f)
        else:
            output = pandas.concat([output, f])

    return output


def init(funk):
    output = funk()
    if output:
        return output


red_light = []

funks = [init_scraper, roxeanne]
output = multi_threader(init, funks, 2)

