#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 14:32:27 2017

@author: william

to do: 
    -wrap into a function
    -Create vector of revevant twiiter pages
    -Automatically assign user to personality categories based on pages
    
    
"""

import tweepy
import time
import pandas as pd

# Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = '929809459576295424-bqkggk2eCOGwG41FjdJJBrDIcmbuWWY'
ACCESS_SECRET = 'PDPKHVValPF5kuLAAid3EM8zJHX19DO1f129aQiIkVKMS'
CONSUMER_KEY = '2YZ3l8upEuXxoTmqZGFXNCafG'
CONSUMER_SECRET = '8AhZnoL9bM1pcLkWAQJ7GZFdPp27YDRyfKImnaHogP3F1taNGC'

#Test account to pull followers from
accountvar = ['wward9', 'LeanneHanson']

#Get autorization to twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)

user_list_df = pd.DataFrame(columns=['User','Page'])


for i in range(0, len(accountvar)):
    
    user_list = []

    #Pull 200 followers per call
    users = tweepy.Cursor(api.followers, screen_name=accountvar[i], count=200).items()

    #Avoid rate limit by waiting 16 minutes every time the limit is reached
    while True:
        try:
            user = next(users)
        except tweepy.TweepError:
            time.sleep(60*16)
            user = next(users)
        except StopIteration:
            break
        user_list.append("@" + user.screen_name)   
    accountvec = [accountvar[i]] * (len(user_list))
    tempdf = pd.DataFrame({'User':user_list, 'Page': accountvec})

    user_list_df = user_list_df.append(tempdf)

    del [user_list, tempdf]