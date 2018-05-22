#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 12:17:35 2018

@author: Michi
"""



import tweepy
import sys
import sys
import json
import twitter
import os

from stream_listener import *


###################################################
#  Keep in the same folder as stream_listener.py
#
# Usage:  from console :  > follow_conversations.py my-input-file.jsonl
# 
# Output : in the directory Replies/ under your current working directory, one file for each conversation
# named replies_to_<tweet.id>.jsonl
###################################################



def get_all_replies(tweet, api, fout, Verbose=False):
        """ Gets all replies to one tweet (also replies-to-replies with a recursive call). Note: tweet is a Status() object """
        
        user = tweet.user.screen_name
        tweet_id = tweet.id
        search_query = '@'+user
        retweet_filter='-filter:retweets'
        query = search_query+retweet_filter
         
        myCursor = tweepy.Cursor(api.search, q=query, 
                                       since_id=tweet_id, max_id=None, 
                                       wait_on_rate_limit=True, 
                                       wait_on_rate_limit_notify=True).items()
        
        
        rep =  [reply for reply in myCursor if reply.in_reply_to_status_id == tweet_id]
            
        if len(rep) !=0:
            for reply in rep:
                if Verbose: 
                    print('Following replies to %s ...' %tweet_id)
                with open(fout, 'a+') as f:
                    f.write(json.dumps(reply._json)+'\n')
                # recursive call to fetch replies-to-replies
                get_all_replies(reply, api, fout, Verbose=False)




def follow_conversations(tweets_file, api, outdir):
    with open(tweets_file, 'r') as f:
        for line in f:
            tweet = twitter.Status.NewFromJsonDict(json.loads(line))
            fout = '%s/replies_to_%s.jsonl' %(outdir, tweet.id)
            get_all_replies(tweet, api, fout, Verbose= False)

            

def main():

    # Get authentication & api
    my_auth = get_auth()
    my_api = get_api(my_auth)

    tweets_file = sys.argv[1] # file where the tweets are stored, read from console

    outdir = os.getcwd()+'Replies'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    follow_conversations(tweets_file, my_api, outdir)
    
    
    
if __name__=='__main__':
    main()