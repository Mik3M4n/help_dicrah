
#################################################
#################################################

# Configuration file for the code 'StreamListener_mm.py'

#################################################
#################################################


######
# Twitter developer credentials (must be valid credentials in string format)
######

consumer_key = 'm9QTUO3kf0GSkhuWqWdVPtwC4'
consumer_secret = 'gQeRqv62UjDer8d3aMMALiFYYFtPquNfoSdlLvXoSElaEq2fuL'
access_token = '992150969604562946-uKKFTtW9a5gQ8LYOyclPPiyufmeAKvc'
access_token_secret = 'MV9bX8zWZzGKsUaIVcaAEc0Aj57ViNAIEJNYTzEa6w108'

######
#  Input parameters - edit these !
######


#  If true, the code will print some updates while running
Verbose = True


#  hashtags or keywords to filter the stream. Must be a list of strings
query = ['#DataScientest'] # a list of strings


# Language to filter the stream.
languages = ['it'] # ex. ['fr']

#  Time limit in seconds.  Must be an integer or None if you don't want any 
time_limit = 30 # an int or None 


# if get_user_tweets = True, the code will save the first n_tweets of the first n_pages of each new user's timeline.

get_user_tweets = True
n_tweets=50
n_pages=4



#####
# Example of output
#####

# data_dir = my_dir/
# query = ['#9Mai']
# languages = ['fr']
# time_limit = 10
# get_user_tweets = True
# n_tweets=50
# n_pages=4

# this will output:
# - the file 'Streams/stream_#9Mai.jsonl' with all tweets containing the hashtag #9mai . Each line(~tweet) is a json.
# - a file 'Users/user_timeline_<username>.jsonl' for every different <usename> that tweeted about your query.
#   In this case we collected 50 tweets * 4 pages  = 200 tweets for each user.
# - a file 'Users/stream_#9Mai_users_list.txt' with a list of the usernames whose tweets we collected


