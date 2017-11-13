#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 14:32:27 2017

@author: william
"""

import sys
import time
import _pickle as cPickle
import twitter
from twitter.oauth_dance import oauth_dance

# Variables that contains the user credentials to access Twitter API 
#ACCESS_TOKEN = '929809459576295424-gNlSOoETSSD7O4wnf74cQ6AvxXrZz0i'
#ACCESS_SECRET = 'RJM7ImJ3nFXsCR94q9UvhfVNFyIcXyRIvuSz2IxTpRqYy'
CONSUMER_KEY = '2YZ3l8upEuXxoTmqZGFXNCafG'
CONSUMER_SECRET = '8AhZnoL9bM1pcLkWAQJ7GZFdPp27YDRyfKImnaHogP3F1taNGC'

SCREEN_NAME = sys.argv[1]
friends_limit = 10000

(oauth_token, oauth_token_secret) = oauth_dance('MiningTheSocialWeb',
    CONSUMER_KEY, CONSUMER_SECRET)
t = twitter.Twitter(domain='api.twitter.com', api_version='1',
                    auth=twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                    CONSUMER_KEY, CONSUMER_SECRET ))

ids = []
wait_period = 2 # sec
cursor = -1

while cursor != 0:
    if wait_period > 3600:
        print ('Too many retries. Saving partial data to disk and exiting')
        f = file('%s.friend_ids' % str(cursor), 'wb') #Needs to be updated for py >2.7
        cPickle.dump(ids, f)
        f.close()
        exit()
    
    try:
        response = t.friends.ids(screen_name=SCREEN_NAME, cursor=cursor)
        ids.extend(response['ids'])
        wait_period = 2 
    except twitter.api.TwitterHTTPError as e:
        if e.e.code == 401:
            print ('Encountered 401 Error (Not Autorized)')
            print ('User %s is protecting their tweets') % (SCREEN_NAME, )
        elif e.e.code in (502, 503):
            print ('Encountered %i Error. Trying again in %seconds' )% (e.e.code,
                wait_period)
            time.sleep(wait_period)
            wait_period *=1.5
            continue
        elif t.account.rate_limit_status()['remaining_hits'] == 0:
            status = t.account.rate_limit_status()
            now = time.time()
            when_rate_limit_resets = status['reset_time_in_seconds']
            sleep_time = when_rate_limit_resets - now
            print ('Rate limit reached. Trying again in %i seconds') % (sleep_time,
                    )
            time.sleep(sleep_time)
            continue
        
cursor = response['next_cusor']
print ('Fetched %i ids for %s') % (len(ids), SCREEN_NAME)
if len(ids) >= friends_limit:
    break
        
print (ids)