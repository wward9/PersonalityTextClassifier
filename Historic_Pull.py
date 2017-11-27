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
import numpy

'''
download and install tor.
Add the below into your torrc file.  Mine was located here: C:\~blaghblagh~\Tor Browser\Browser\TorBrowser\Data\Tor
    ControlPort 9051
    HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE


Also, tor does need to be running in the background.  Will make it open on initiation later. if i feel like it....


looks like new ip requests need to be staggered, or else the same ip is given

'''

''' Change these paths to something local.  Best keep them out of the Git Repository I think '''
path1 = r'C:\Users\Ureridu\Desktop\Twitter/Users/'
path2 = r'C:\Users\Ureridu\Desktop\Twitter/user_tweets/'


def roxeanne():
    global red_light
    while 1:
        time.sleep(1)
        if red_light:
            out = red_light.pop(0)
            time.sleep(3)

            if out == 'done':
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
        data = scrape_code(bowser, site)
#        bowser.close()

    except Exception as e:
        print(e)

    return data


def xpath_get(bowser, element, xpath, attrib):
    bad_count = 0
    while 1:
        try:
            elem = element.find_element_by_xpath(xpath)
            if attrib == 'text':
                item = elem.text
            elif attrib:
                item = elem.get_attribute(attrib)
            else:
                item = elem
            break
        except Exception as e:
            if bad_count >= 5:
                item = e
                print(e, xpath, attrib)
                break
            bad_count += 1
    return item


def scrape_code(bowser, site):
    global path1
    global path2

    *_, user = site.split('/')
    user_data_xpaths = [['//h1[@class="ProfileHeaderCard-name"]/a', 'text'],
                        ['//*[contains(@class, "ProfileHeaderCard-bio u-dir")]', 'text'],
                        ['//*[contains(@class, "ProfileHeaderCard-joinDateText js-tooltip u-dir")]', 'text'],
                        ['//*[contains(@class, "ProfileHeaderCard-screenname u-inlineBlock u-dir")]/a', 'text'],
                        ['//li[contains(@class, "ProfileNav-item ProfileNav-item--tweets is-active")]/a', 'text'],
                        ['//li[contains(@class, "ProfileNav-item ProfileNav-item--following")]/a', 'text'],
                        ['//li[contains(@class, "ProfileNav-item ProfileNav-item--followers")]/a', 'text'],
                        ['//li[contains(@class, "ProfileNav-item ProfileNav-item--favorites")]/a', 'text'],
                        ['//div[@class="ProfileCanopy-headerBg"]/img', 'src'],
                        ['//div[@class="ProfileAvatar"]/a/img', 'src'],
                        ['//*[contains(@class, "ProfileHeaderCard-urlText u-dir")]', 'text'],
                        ['//*[contains(@class, "ProfileHeaderCard-locationText u-dir")]', 'text'],
                        ['//*[contains(@class, "PhotoRail-headingText PhotoRail-headingText--withCount")]/a', 'text'],
                        ]

    user_data = []
    for xpath, attrib in user_data_xpaths:
        try:
            *_, item = xpath_get(bowser, bowser, xpath, attrib).split('\n')
        except Exception as e:
            item = None
        user_data.append(item)

    user_data = numpy.array(user_data).reshape(1, 13)
    cols = ['user_name', 'bio', 'join_date', 'user_id', 'num_tweets', 'following', 'followers', 'likes', 'avatar_pic', 'header_pic', 'location', 'links', 'num_media']
    user_data = pandas.DataFrame(user_data, columns=cols)
    file_name = user_data.get_value(0, 'user_name') + '_' + user + '.xlsx'
    writer = pandas.ExcelWriter(path1 + file_name)
    user_data.to_excel(writer, 'user data')

    stable_count = 0
    old_num = 0
    while 1:
        tweets = bowser.find_elements_by_xpath('//li[@data-item-type="tweet"]')
        new_num = len(tweets)
        bowser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(randint(2, 3))
        if new_num == old_num:
            stable_count += 1
            if stable_count >= 6:
                break
        old_num = new_num

    all_tweet = []
    for tweet in tweets:
        one_tweet = [user]

        tweet_json = tweet.find_element_by_xpath('./div')
        json_info = tweet_json.get_attribute('data-reply-to-users-json')
        tweet_id = tweet_json.get_attribute('data-tweet-id')

        
        one_tweet.append(user_data.get_value(0, 'user_id'))
        one_tweet.append(json_info)
        one_tweet.append(tweet_id)

        tweet_xpaths = [
                        ['.//div[@class="js-tweet-text-container"]/p', 'text'],
                        ['.//*[contains(@id, "profile-tweet-action-reply-count")]', 'text'],
                        ['.//*[contains(@id, "profile-tweet-action-retweet-count")]', 'text'],
                        ['.//*[contains(@id, "profile-tweet-action-favorite-count")]', 'text'],
                        ['//*[@class="stream-item-header"]/small/a', 'data-original-title'],
                        ]

        for xpath, attrib in tweet_xpaths:
            item = xpath_get(bowser, tweet, xpath, attrib)
            one_tweet.append(item)

        try:
            images = [image.get_attribute('aria-label') for image in tweet.find_elements_by_xpath('.//div[@class="js-tweet-text-container"]/p/img')]
        except Exception as e:
#            print('emoji', e)
            images = []
        one_tweet.append(images)

        try:
            hashtags = [hashtag.text for hashtag in tweet.find_elements_by_xpath('.//div[@class="js-tweet-text-container"]/p/a') if hashtag.get_attribute('data-query-source') == "hashtag_click"]
        except Exception as e:
#            print('hashtag', e)
            hashtags = []
        one_tweet.append(hashtags)

        try:
            tweet_images_box = tweet.find_element_by_xpath('.//*[@class="AdaptiveMediaOuterContainer"]')
            tweet_images = tweet_images_box.find_elements_by_xpath('.//img')
            tweet_image_links = [tweet_image.get_attribute('src') for tweet_image in tweet_images]
        except Exception as e:
#            print('IMAGE', e)
            tweet_image_links = []
        one_tweet.append(tweet_image_links)

        all_tweet.append(one_tweet)
#        break

#    print(one_tweet)
    tweet_cols = ['user', 'user_id', 'json_info', 'tweet_id', 'tweet_text', 'replies', 'retweets', 'likes', 'timestamp', 'emojis', 'hashtags', 'images']
    all_tweet = pandas.DataFrame(all_tweet, columns=tweet_cols)
    file_name = user + '_' + 'tweets.xlsx'
    writer = pandas.ExcelWriter(path2 + file_name)
    all_tweet.to_excel(writer, 'user data')

    return all_tweet


def init_scraper():
#    site_list = ["https://httpbin.org/ip" for i in range(12)]
#    site_list = ["https://twitter.com/do1cefarniente" for i in range(1)]
    site_list = pandas.read_excel('Users.xlsx')['Users']
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

