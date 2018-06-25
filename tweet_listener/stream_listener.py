#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Created on Mon May 14 09:33:43 2018

@author: Michi
@contributors: Alex, Ed

To configure parameters and queries, please edit the file config.py where an explanation is provided.
Depending on your query, the output will be in the directories:
Streams/ , for the streaming filtered by the query (with/without replies & label prediction)
Users/ , for users' timelines
"""

####### References:

# https://media.readthedocs.org/pdf/tweepy/latest/tweepy.pdf
# http://ebook.pldworld.com/_eBook/-Packt%20Publishing%20Limited-/9781783552016-MASTERING_SOCIAL_MEDIA_MINING_WITH_PYTHON.pdf
# http://stats.seandolinar.com/collecting-twitter-data-using-a-python-stream-listener/ 

# Code of the StreamListener class:
# https://github.com/tweepy/tweepy/blob/78d2883a922fa5232e8cdfab0c272c24b8ce37c4/tweepy/streaming.py






############################################################################
############################################################################



import tweepy, sys, json, config, time, os, twitter, urllib, sys
if sys.version_info[0] < 3:
    import pickle
else:
    import dill as pickle
    #import cPickle as pickle

sys.path.insert(0, '../machine_learning')
from help_dicrah_functions import *





###################
# 1. Get authentication & api
###################


def get_auth():
    """
    Gets twitter authentication. Credentials are imported from the config.py file
    """
    try:
        auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
        auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    except KeyError:
        sys.stderr.write('Set valid twitter variables!')
        sys.exit(1)

    return auth


def get_api(auth):
    """
    Sets the API given the twitter autorization auth
    """
    api = tweepy.API(auth)
    return api



###################
# 2. Customize the StreamListener tweepy class
###################


class myListener(tweepy.StreamListener):

    def __init__(self, api=None, time_limit=None, 
                 get_user_tweets=False, follow_conversations=False, replies_only=False, origin_only=False, max_depth=10,
                 predict_tweet=False, save_predictions=True):
        
        self.api = api
        self.inTime = time.time()
        if time_limit == None:
            self.time_limit = float('inf')
        else:
            self.time_limit = time_limit
        self.time_to_go = self.time_limit
        
        # output directory
        self.query_fname = config.query_fname
        self.data_dir_stream = os.getcwd() + '/Streams'
        if not os.path.exists(self.data_dir_stream):
            os.makedirs(self.data_dir_stream)
        self.fout_stream = '%s/stream_%s.jsonl' % (self.data_dir_stream, self.query_fname)
        
        self.get_user_tweets = get_user_tweets
        self.follow_conversations = follow_conversations
        self.replies_only = replies_only
        self.origin_only = origin_only
        self.max_depth = max_depth
        self.predict_tweet = predict_tweet
        
        if self.predict_tweet:
            self.model = pickle.load(open(config.my_classifier, 'rb'))
            if config.Verbose:
                print ('Model used to predict tweet label:')
                print (self.model)
            self.my_vectorizer = pickle.load(open(config.my_vectorizer, 'rb'))
            self.save_predictions = save_predictions
       
        if self.get_user_tweets:
            self.data_dir_users = os.getcwd() + '/Users'
            if not os.path.exists(self.data_dir_users):
                os.makedirs(self.data_dir_users)
        return

    
    def on_status(self, status):
        if status.retweeted_status:
            return

    def on_data(self, data):
        """Possible options are: save all tweets containing query words,
           follow conversations with all replies, search for query words in replies only,
           predict if a tweet contains hateful/racist content.
           See config.py for configuring the options.
        """
        while self.time_to_go > 0:
            self.new_time_to_go = self.inTime + self.time_limit - time.time()
            try:
                
                if config.Verbose and self.time_to_go - self.new_time_to_go > 10:
                    print (' ---- %s seconds to go... ' % str(self.new_time_to_go))
                
                data_status = twitter.Status.NewFromJsonDict(json.loads(data))
                
                # 1 - look for query words in tweets
                if not self.replies_only and not self.predict_tweet:
                    
                    # A - save
                    with open(self.fout_stream, 'a+') as (f):
                        f.write(json.dumps(data_status._json) + '\n')
                    
                    # B - save tweets by the user
                    if self.get_user_tweets:
                        data = json.loads(data)
                        self._get_user_tweets(data, config.n_tweets_user, config.n_pages_user)
                        
                    # C - follow the conversation 
                    if self.follow_conversations and self._is_reply(data_status):
                        if config.Verbose:
                            print ('Following conversation containing the reply:\n %s' % data_status.text)
                        tweet = self.find_source(data_status, self.fout_stream)
                        self.get_all_replies(tweet, self.api, self.fout_stream, depth=self.max_depth, Verbose=config.Verbose)
                
                
                else: # 2 - look for query words in replies only
                    if not self.predict_tweet and self._is_reply(data_status):
                        if config.Verbose:
                            print ('Conversation found with target word in a reply! Text: \n %s' % data_status.text)
                        if self.origin_only:
                            in_reply_to = self.api.get_status(data_status.in_reply_to_status_id, tweet_mode='extended', full_text=True)
                            if config.Verbose:
                                print ('Replying to:\n %s' % in_reply_to.full_text)
                            with open(self.fout_stream, 'a+') as (f):
                                f.write(json.dumps(in_reply_to._json) + '\n')
                        else:
                            tweet = self.find_source(data_status, self.fout_stream)
                            self.get_all_replies(tweet, self.api, self.fout_stream, depth=self.max_depth, Verbose=config.Verbose)
                    
                    
                    else: # 3 - predict the content of the tweet with ML
                        if self.predict_tweet:
                            
                            my_text = data_status.text
                            if sys.version_info[0] < 3:
                                try:
                                    my_text = my_text.encode('utf-8')
                                except UnicodeDecodeError:
                                    my_text = my_text.encode('latin-1')

                            pred = self.predict_sentiment(my_text)
                            if pred == 0:
                                print ('!!!!! Suspect tweet found !!!!!')
                                print ('Text: %s' % data_status.text)
                                print ('Predicted label: %s' % pred)
                            if pred == 1:
                                print ('Text: %s' % data_status.text)
                                print ('Predicted label: %s' % pred)
                            if self.save_predictions:
                                tweet_with_label = data_status
                                tweet_with_label._json[u'Predicted_label'] = int(pred[0])
                                with open(self.fout_stream, 'a+') as (f):
                                    f.write(json.dumps(tweet_with_label._json) + '\n')
                
                # update time and continue
                self.time_to_go = self.new_time_to_go
                return True
            
            # handle exceptions
            except BaseException as e:
                sys.stderr.write(('Error on_data: {}\n').format(e))
                self.time_to_go = self.new_time_to_go
                time.sleep(5)
            except ProtocolError as pe:
                sys.stderr.write(('Error on_data: {}\n').format(e))
                self.time_to_go = self.new_time_to_go
                print ('Sleeping for 10 seconds...')
                time.sleep(10)
            except tweepy.TweepError as e:
                sys.stderr.write(('Error on_data: {}\n').format(e))
                self.time_to_go = self.new_time_to_go
                time.sleep(5)

        # if time ends, stop
        return False

   
    def predict_sentiment(self, my_text):
        """
        Given the text of a tweet as a string, predicts the label : 
        0 for "hateful/racist", 1 for "Neutral".
        The prediction is based on the model described in the folder machine_learning.
        Features are built according to the same method as explained in the notebook.
        """
        if config.Verbose:
               print( 'Building features for predicting label...')
                            
        tw_data = pd.DataFrame([my_text], columns=['Texte'])
        tw_data['Texte_clean'] = tw_data.Texte.apply(lambda x: (' ').join(tokenize(tweet_cleaner(x, my_dict))))
        features_tfidf = self.my_vectorizer.transform(tw_data.Texte_clean)
        tw_data = add_lexical_features(tw_data)
        lex_cols = [
         'nbr_characters', 'nbr_words', 'nbr_ats', 'nbr_hashtags', 'nbr_urls',
         'nbr_letters', 'nbr_caps', 'nbr_fancy']
        lex_features = tw_data.as_matrix(columns=lex_cols)
        M1 = np.concatenate([features_tfidf, lex_features], axis=1)
        pred = self.model.predict(M1)
        return pred

    def _get_full_tweet(self, tweet_id):
        """
        Fetches tweet in extended mode
        """
        my_tw = self.api.get_status(tweet_id, tweet_mode='extended', full_text=True)
        return my_tw

    def on_error(self, status):
        """Stops the execution if we are limited by the twitter API"""
        if status == 420:
            sys.stderr.write('Rate limit exceeded\n')
            return False
        sys.stderr.write(('Error {}\n').format(status))
        return True

    def get_all_replies(self, tweet, api, fout, depth=10, Verbose=False):
        """ Gets all replies to one tweet (also replies-to-replies with a recursive call).
        Note: tweet is a Status() object 
        """
        if depth < 1:
            print( 'Max depth reached')
            return
        user = tweet.user.screen_name
        tweet_id = tweet.id
        search_query = '@' + user
        retweet_filter = '-filter:retweets'
        query = search_query + retweet_filter
        try:
            myCursor = tweepy.Cursor(api.search, q=query, since_id=tweet_id,
                                     max_id=None, wait_on_rate_limit=True, 
                                     wait_on_rate_limit_notify=True, 
                                     tweet_mode='extended', full_text=True).items()
            rep = [ reply for reply in myCursor if reply.in_reply_to_status_id == tweet_id ]
        except tweepy.TweepError as e:
            sys.stderr.write(('Error get_all_replies: {}\n').format(e))
            time.sleep(60)

        if len(rep) != 0:
            if Verbose: 
                if hasattr(tweet, 'full_text'):
                    print ('Saving replies to: %s' % tweet.full_text)
                elif hasattr(tweet, 'text'):
                    print ('Saving replies to: %s' % tweet.text)
            for reply in rep:
                with open(fout, 'a+') as (f):
                    data_to_file = json.dumps(reply._json)
                    f.write(data_to_file + '\n')
                self.get_all_replies(reply, api, fout, depth=depth - 1, Verbose=False)

        return

    def _worth_to_follow(self, tweet, wordList):
        """
        Checks if tweet contains one of the words in wordList. Returns a boolean
        """
        if self._is_reply(tweet) and any((word in tweet.text for word in wordList)):
            return True
        return False

    def _is_reply(self, tweet):
        """
        Checks if tweet is a reply. Returns a boolean
        """
        if tweet.in_reply_to_status_id == None:
            return False
        return True
        return

    def find_source(self, tweet, fout, max_height=100):
        """ If a tweet is a reply, find the origin of the conversation"""
        original_tw = self.api.get_status(tweet.in_reply_to_status_id, 
                                          tweet_mode='extended', 
                                          full_text=True)
        if original_tw.in_reply_to_status_id == None:
            tweet = original_tw
        else:
            tweet = self.find_source(original_tw, fout, max_height=max_height - 1)
        with open(fout, 'a') as (f):
            f.write(json.dumps(tweet._json) + '\n')
        return tweet

    def _get_user_tweets(self, data, n_tweets, n_pages):
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
                print ('Saving tweets by %s...' % user)
            outfile = '%s/user_timeline_%s.jsonl' % (self.data_dir_users, user)
            try:
                with open(outfile, 'w') as (f):
                    for page in tweepy.Cursor(self.api.user_timeline,
                                              screen_name=user, 
                                              count=n_tweets, tweet_mode='extended', 
                                              full_text=True).pages(n_pages):
                        for tweet in page:
                            f.write(json.dumps(tweet._json) + '\n')

            except BaseException as e:
                sys.stderr.write(('Error save_user_tweets: {}\n').format(e))
                time.sleep(5)
            except ProtocolError as pe:
                sys.stderr.write(('Error on_data: {}\n').format(e))
                self.time_to_go = self.new_time_to_go
                print ('Sleeping for 10 seconds...')
                time.sleep(10)


            
###################
# 3. main function: set and start the stream/filter
###################

                
                
def main():
    my_auth = get_auth()
    my_api = get_api(my_auth)
    if config.Verbose:
        print ('-----')
        if config.query != []:
            print( 'Starting streaming for the query in %s' % config.query_file)
        if config.languages != []:
            print ('Languages: %s' % config.languages)
        if config.time_limit == None:
            print ('No time limit')
        else:
            print ('Time limit: %s seconds' % config.time_limit)
        if config.get_user_tweets:
            print ('Downloading %s tweets for each new user' % config.n_tweets_user * config.n_pages_user)
        else:
            print( "Users' tweets not requested")
        if config.follow_conversations:
            print ('Getting replies to tweets and folowing conversations with target words: %s' % config.query_replies)
        else:
            print ('Replies to tweets not requested')
        if config.replies_only:
            print ('Getting only conversations where a reply contains one of the words in query_replies')
        print( '-----')
        if config.predict_tweet:
            print ('Predicting labels for tweets.... \n Estimator:')
   
    my_stream = tweepy.Stream(my_auth, 
                              myListener(api = my_api, 
                                         time_limit = config.time_limit, 
                                         get_user_tweets = config.get_user_tweets,
                                         follow_conversations = config.follow_conversations, 
                                         replies_only = config.replies_only, 
                                         max_depth = config.max_depth,
                                         origin_only = config.origin_only, 
                                         predict_tweet = config.predict_tweet,
                                         save_predictions = config.save_predictions), 
                              tweet_mode='extended', full_text=True)
    if not config.predict_tweet:
        if config.replies_only:
            my_stream.filter(track=config.query_replies, 
                             languages=config.languages, 
                             async=True, 
                             stall_warnings=True)
        else:
            my_stream.filter(track=config.query,
                             languages=config.languages,
                             async=True,
                             stall_warnings=True)
    else:
        my_stream.filter(#locations=config.GEOBOX,
                         track=config.query_replies,
                         languages=config.languages, 
                         async=True, 
                         stall_warnings=True)
    
    return




###################
# Execute
###################



if __name__ == '__main__':
    main()
