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
import queue

'''
download and install tor.
Add the below into your torrc file.  Mine was located here: C:\~blaghblagh~\Tor Browser\Browser\TorBrowser\Data\Tor
    ControlPort 9051
    HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE


Also, tor does need to be running in the background.  Will make it open on initiation later. if i feel like it....


looks like new ip requests need to be staggered, or else the same ip is given

'''


def roxeanne():
    global Q
    global avail

    while 1:
        if not Q.empty():
            avail.append(Q.get())
            time.sleep(9)
        time.sleep(1)
        if avail and avail[0] == 'done':
            print('finished')
            break


def init_torified_bowser():
    look = 1
    c = 0
    while look:
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password='16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE')
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
        executor.map(funk, site_list, timeout=15)


def scraper(site):
    global Q
    global avail
    ident = threading.get_ident()
    Q.put(ident)

    while ident not in avail:
        #print(avail)
        time.sleep(1)
    avail.remove(ident)

    print(ident)

    bowser = init_torified_bowser()
    bowser.get(site)
    time.sleep(5)
    bowser.close()


def init_scraper():
    site_list = ["https://httpbin.org/ip" for i in range(4)]
    multi_threader(scraper, site_list, 4)
    Q.put('done')


def init(funk):
    funk()


Q = queue.Queue()
avail = []

funks = [init_scraper, roxeanne]
multi_threader(init, funks, 2)

