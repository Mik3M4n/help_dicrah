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



def follow_conversations(tweets_file, api, outdir):
        for line in open(tweets_file):
            tweet = twitter.Status.NewFromJsonDict(json.loads(line))
            print('Tweet text: '+tweet.text)
            print('Tweet id: %s' %tweet.id)
            fout = '%s/replies_to_%s.jsonl' %(outdir, tweet.id)
            
            listener = myListener(api = api)
            listener.get_all_replies(tweet, api, fout, Verbose= True)

            

def main():

    # Get authentication & api
    my_auth = get_auth()
    my_api = get_api(my_auth)
    
    
    tweets_file = sys.argv[1] # file where the tweets are stored, read from console

    outdir = os.getcwd()+'/Replies'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    follow_conversations(tweets_file, my_api, outdir)
    
    
    
if __name__=='__main__':
    main()