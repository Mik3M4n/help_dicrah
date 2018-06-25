"""
Created on Mon May 14 09:30:52 2018

@author: Michi
@contributors: Alex, Ed
"""


############################################
# Configuration file for stream_listener
############################################

# Please note that the code does not yet supply a check of the correctness of the input variables' format
# So, to avoid errors, please be careful to give to all variables valid values.

############################################


# Get twitter credentials. The credentials must be in the file Credentials.csv in the order:
# CONSUMER_KEY
# CONSUMER_SECRET
# ACCESS_TOKEN
# ACCESS_TOKEN_SECRET

credentialsFile = 'Credentials2.csv'
credentials = open(credentialsFile, 'r')
CONSUMER_KEY = credentials.readline().strip()
CONSUMER_SECRET = credentials.readline().strip()
ACCESS_TOKEN = credentials.readline().strip()
ACCESS_TOKEN_SECRET = credentials.readline().strip()
credentials.close()

# Name of the output file of the query. This will be in the directory Streams/
query_fname = 'prova_25'

# Print updates while running
Verbose = True

# File where the query words are stored. In case of a simple query (e.g.) an hasthag,
# this can be entered directly in the form of a list, e.g. query = ['<your_hashtag>']
# Must be a list of strings
query_file = 'query_words.txt'
query = []
with open(query_file, 'r') as (f):
    for line in f:
        query.append(line)

        
# Language
languages = [ 'fr']

#  Time limit in seconds.  Must be an integer or None if you don't want any
time_limit = 45000


# If tweets are replies, fetch the entire conversation
follow_conversations = False


# If fetches conversations, we can choose to get only the tweet in reply to, or
# to look for query wrds in reply only, and the max number of replies 
replies_only = False
origin_only = False
max_depth = 10
# Query words to look in replies 
query_replies = ['#Racisme', '#RacismeOrdinaire', 'raciste', 'dilcrah', 'pharos', 'balancetonraciste', 'balancetonracisme', 'sioniste']



# Look for teh first n_tweets_user in the first n_pages_user for each user found.
# Output will be in the folder Users/ in the format:
# user_timeline_<username>.jsonl

get_user_tweets = False
n_tweets_user = 300
n_pages_user = 5



# Machine learning: predict the content of the tweet: 0 for racist/hateful, 1 for neutral 
# We can choose to save predictions in the query file
# The label will be contained in an additional field in the tweet dict in json format, called 'Predicted_label'
# e.g. tweet['Predicted_label']


predict_tweet = True
save_predictions = True
my_classifier = '../machine_learning/finalized_model_fr.pk'
my_vectorizer = '../machine_learning/my_vectorizer.pk'

# geographical area where to launch the query if asking for predictions ([ -180, -90, 180, 90] is the entire world)
GEOBOX = [ -180, -90, 180, 90]





############################################
# Example of output
############################################

# query_fname = 'ex_query'
# data_dir = my_dir/
# query = ['#9Mai']
# languages = ['fr']
# time_limit = 10
# get_user_tweets = True
# n_tweets=50
# n_pages=4

# this will output:
# - the file 'Streams/stream_ex_query.jsonl' with all tweets containing the hashtag #9mai . Each line(~tweet) is a json.
# - a file 'Users/user_timeline_<username>.jsonl' for every different <usename> that tweeted about your query.
#   In this case we collected 50 tweets * 4 pages  = 200 tweets for each user.
# - a file 'Users/stream_ex_query_users_list.txt' with a list of the usernames whose tweets we collected
