#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 11:09:12 2018

@author: Michi
"""


# To run the code, edit the file config.py with the following global variables:
# - your query (list of hashtags/keywords)
# - your language
# - your time limit
# - if you want to save tweets of every new user you find in the streaming, and if so how many
# No need to change anything in the code below!


# The output will be in the directories  Streams/ and Users/ under your current working directory; for the output format, see explanation in config.py


# References:

# https://media.readthedocs.org/pdf/tweepy/latest/tweepy.pdf
# http://ebook.pldworld.com/_eBook/-Packt%20Publishing%20Limited-/9781783552016-MASTERING_SOCIAL_MEDIA_MINING_WITH_PYTHON.pdf
# http://stats.seandolinar.com/collecting-twitter-data-using-a-python-stream-listener/ 

# Code of the StreamListener class:
# https://github.com/tweepy/tweepy/blob/78d2883a922fa5232e8cdfab0c272c24b8ce37c4/tweepy/streaming.py




############################################################################
############################################################################

import tweepy
import sys
import json
import config
import time
import os




###################
# 1. Get authentication & api
###################


def get_auth():
    """
    Gets twitter authentication. Credentials are imported from the config.py file
    """
    try:
        auth = tweepy.OAuthHandler(config.consumer_key,config.consumer_secret )
        auth.set_access_token(config.access_token, config.access_token_secret)
        
    except KeyError: 
        sys.stderr.write('Set valid twitter variables!')
        sys.exit(1)
        
    return auth


def get_api(auth):
    api = tweepy.API(auth)
    return api




###################

# 2. Customize the StreamListener

# An instance of tweepy.Stream establishes a streaming session and routes messages to StreamListener instance. 
# The on_data method of a stream listener receives all messages and calls functions according to the message type.
# The default StreamListener can classify most common twitter messages and routes them to appropriately named methods, 
# but these  methods are only stubs.
# Therefore using the streaming api has three steps.
# 1. Create a class inheriting from StreamListener 
# 2. Using that class create a Stream object
# 3. Connect to the Twitter API using the Stream.

###################





                

class myListener(tweepy.StreamListener):
    
    
    def __init__(self, api = None, time_limit = None, get_user_tweets = False):
        
        self.api = api
        self.inTime = time.time()    
        if time_limit == None:  # if no time limit is passed, don't put any
            self.time_limit = float('inf')
        else:
            self.time_limit = time_limit
        self.time_to_go = self.time_limit
        
        self.query_fname = '_'.join(config.query)
        self.data_dir_stream = os.getcwd()+'/Streams'
        if not os.path.exists(self.data_dir_stream):
            os.makedirs(self.data_dir_stream)
        self.fout_stream = "%s/stream_%s.jsonl" % (self.data_dir_stream, self.query_fname)
        
        self.get_user_tweets = get_user_tweets
        
        if self.get_user_tweets:
            self.data_dir_users = os.getcwd()+'/Users'
            if not os.path.exists(self.data_dir_users):
                os.makedirs(self.data_dir_users)
            self.fout_userlist = "%s/stream_%s_users_list.txt" % (self.data_dir_users, self.query_fname)
            self.users=[]  
        
        
         
    
    
    def on_data(self, data): 
        # The on_data() method is called when data is coming through. 
        # This function simply stores the data as it is received in a .jsonl file. Each line of  
        # this file will then contain a single tweet, in the JSON format. 
        # Once the data is written, we will return True to continue the execution, until the time limit (if any) is reached.
        # If anything goes wrong in this process, we will catch any exception, print a message on stderr,
        # put the application to sleep for five seconds, and then continue the execution by returning True again
        
        
        while self.time_to_go > 0:
            self.new_time_to_go = self.inTime + self.time_limit - time.time()
              
            try:
                if config.Verbose and (self.time_to_go-self.new_time_to_go)>10:
                    print(" ---- %s seconds to go... " %str(self.new_time_to_go))
                
                with open(self.fout_stream, 'a') as f: #saves tweets. Note that with 'a' 
                                                        #every time we re-run the code with the same query, 
                                                         #the tweets will be appended
                    f.write(data)
                             
                if self.get_user_tweets: # if we requested to save tweet of each user found, do that
                    data = json.loads(data) # needed to have a dict (otherwise data is in unicode format)
                    self._save_user_tweets(data, config.n_tweets, config.n_pages)
                
                self.time_to_go = self.new_time_to_go
               
                return True
                
            except BaseException as e:
                sys.stderr.write("Error on_data: {}\n".format(e))
                self.time_to_go = self.new_time_to_go
                time.sleep(5)
            
            
        if self.get_user_tweets: # at the end, saves the usernames in a txt files
            with open(self.fout_userlist,'a') as f:
                f.write('# Users list for the query: %s \n' %self.query_fname)
                for item in self.users:
                    f.write("{}\n".format(item))
            if config.Verbose:
                print('-----')
                print('List of users: %s' %self.users)
                print('-----')
                
        return False


    def on_error(self, status):
        # The on_error() method in particular will deal with explicit errors from Twitter
        # When using Twitter’s streaming API one must be careful of the dangers of rate limiting. 
        # If clients exceed a limited number of attempts to connect to the streaming API in a window of time, 
        # they will receive error 420. The amount of time a client has to wait after receiving error 420 will 
        # increase exponentially each time they make a failed attempt.
        # Our implementation of the on_error() method will stop the execution only if there's error 420, 
        # meaning that we have been rate limited by the Twitter API. 
        
        if status == 420:
            sys.stderr.write("Rate limit exceeded\n")
            return False
        else:
            sys.stderr.write("Error {}\n".format(status))
            return True
 
   
    def _save_user_tweets(self, data, n_tweets, n_pages):
    
        """ 
        Saves the first n_tweets of the first n_pages on the timeline of the given user. 
        Stores them in a file in jsonl format name 'user_timeline_***.jsonl'where *** is the username
        E.g. save_user_tweets(EmmanuelMacron, api, 20, 2) saves the first 20 tweets in the first 2 pages of
        E. Macron's timeline in the file user_timeline_EmmanuelMacron.jsonl
        """
        
        user = str(data['user']['screen_name'])
        if user not in self.users:
            self.users.append(user)
            if config.Verbose:
                print('Saving tweets by %s...' %user)
            outfile ="%s/user_timeline_%s.jsonl" % (self.data_dir_users, user)
            try:
                with open(outfile, 'w') as f:
                    for page in tweepy.Cursor(self.api.user_timeline, screen_name = user, count = n_tweets).pages(n_pages):
                        for tweet in page:
                            f.write(json.dumps(tweet._json)+'\n')
            except BaseException as e:
                sys.stderr.write("Error save_user_tweets: {}\n".format(e))
                time.sleep(5)
                
            






###################
# 4. Start the stream
###################


def main():
    
    # Get authentication & api
    my_auth = get_auth()
    my_api = get_api(my_auth)
    
       
    # Print a summary of the query
    if config.Verbose:
        print('-----')
        if config.query != []:
            print('Starting streaming for the hashtags: %s' %config.query)
        if config.languages != []:
            print ('Languages: %s' %config.languages)
        if config.time_limit == None:
            print('No time limit')
        else:
            print('Time limit: %s seconds' %config.time_limit)
        print('-----')
    
    # Stream
    my_stream = tweepy.Stream(my_auth, 
                              myListener(api = my_api, time_limit = config.time_limit, 
                                         get_user_tweets = config.get_user_tweets))
    
    my_stream.filter(track = config.query, languages = config.languages, async=True)





###################
# Execute
###################


if __name__ == '__main__':
    
    # Uncomment the line below to start the streaming
    main()
    
    
    