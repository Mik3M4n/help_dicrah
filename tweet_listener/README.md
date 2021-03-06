
# STREAM LISTENER



## Description

stream_listener.py is a code to scrape twitter. It launches a streaming filtered by different options, including query words and prediction of sentiment based on a pre-trained classifier.
Details are explained below.
The language is French. 

DISCLAIMER: the pre-trained models for sentiment analysis do not fit the GitHub repo. We could provide them to anyone interested upon request. 

## Running and options

To set parameters and select the running mode, please edit the config.py file where explanation is provided. Do not edit the code in stream_listener.py unless you want to extend it.


A summary of the available options (with the corresponding variables' values, to be set in config.py) is provided here.

The options are: (1) look for tweets filtered by a query word list, (2) look for replies containing words in a query word list and analyse the corresponding conversation, or (3) predict their sentiment ('hateful/racist' or 'neutral') according to a ML classifier provided as input. In case (1), you can also choose the option of looking for replies.


Here we provide a more detailed explanation of the three options, and the values of the corresponding parameters to set in config.py

(1) Look for target words in ALL INCOMING TWEETS:

A: save all
   - replies_only = False
   - save_data = True

B : if you want to also save the first n_tweets for each of the first n_pages of each user’s timeline:

  - self.get_user_tweets = True

  - set n_tweets_user and n_pages_user to the desired value

C: if you want to also track the conversation: 
   - follow_conversations = True

   - In this case, for each tweet the listener will check if the tweet is a reply (or has replies), fetch the origin of the conversation and save the tweets.


(2) if you want to look for target words in REPLIES ONLY:

- save_data = True
- if you only want to save the origin of the conversation: origin_only=True
- query words are set in the variable query_replies


For both points 1 and 2, you can set also the max depth of a conversation, i.e. the maximun number of replies to fetch, in the variable max_depth.


(3) If you want to PREDICT the sentiment of incoming tweets:

- predict_tweet = True
- input the geographical zone where you want to look for tweets in the variable GEOBOX in config.py
- choose whether to save data with save_data
- choose whether to save predictions with save_predictions. In this case, the output will be the same format as point (1) but with an additional field for the predicted label.
- The code will print alerts for "suspects" tweets.




## Output

The output will be in the folder(s) Streams,and Users, under your current directory. For details about settings and name of the output files, see config.py

All the queries are saved in .jsonl format (one tweet per line in json format)



## Notes and improvements

* The option of following conversation works, but it may be inefficients in terms of time and handling of Twitter API rate limits. This may become a problem if following very popular hashtag/very active conversations/very active prophiles .Consider this elements before using it blindly !

* The output of label predictions is for the moment only an alert printed on the terminal. This may be improved.

* Handle check of input variables




## References:

*  https://media.readthedocs.org/pdf/tweepy/latest/tweepy.pdf
*  http://ebook.pldworld.com/_eBook/-Packt%20Publishing%20Limited-/9781783552016-MASTERING_SOCIAL_MEDIA_MINING_WITH_PYTHON.pdf
*  http://stats.seandolinar.com/collecting-twitter-data-using-a-python-stream-listener/ 
*  https://github.com/tweepy/tweepy/blob/78d2883a922fa5232e8cdfab0c272c24b8ce37c4/tweepy/streaming.py

