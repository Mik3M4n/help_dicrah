# -*- coding: utf-8 -*-
"""
Created on Tue May  8 16:54:56 2018

@author: Alex
"""

import time
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
import io
import sys
import os

#VARIABLES GLOBALES
#Gestion des fichiers locaux
credentialsFile = 'Credentials.csv'
dataFile = 'DataTweets.json'

#Gestion des mots-clés recherchés
keyword_list = ['haine, race'] #track list


#Définition des noms qualifiés des fichiers locaux
FQdatafile = os.getcwd() + '/' + dataFile
FQdataCredentials = os.getcwd() + '/' + credentialsFile 

#Réupération des credentials twitter
credentials = open(FQdataCredentials, 'r') 
CONSUMER_KEY = credentials.readline().strip()
CONSUMER_SECRET = credentials.readline().strip()
ACCESS_TOKEN = credentials.readline().strip()
ACCESS_TOKEN_SECRET = credentials.readline().strip()
credentials.close()

#Définition du début de la période "d'écoute" de Twitter
start_time = time.time()


#ETAPE 1 - AUTHENTIFICATION TWITTER
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#Boucle d'écoute de Twitter, basée sur la classe StreamListener
#Crédit : http://stats.seandolinar.com/collecting-twitter-data-using-a-python-stream-listener/
class listener(StreamListener):
   def __init__(self, start_time, time_limit=60):
       self.time = start_time
       self.limit = time_limit
       self.tweet_data = []
   def on_data(self, data):
       while (time.time() - self.time) < self.limit:
           try:
               print(start_time + self.limit - time.time())
               self.tweet_data.append(data)
               return True
           except BaseException as e:
               print('failed ondata,', str(e))
               time.sleep(5)
               pass
       saveFile = io.open(FQdatafile, 'a', encoding='utf-8')
#       saveFile.write(u'[\n')
#       saveFile.write(','.join(self.tweet_data))
       saveFile.write(''.join(self.tweet_data))
#       saveFile.write(u'\n]')
       saveFile.close()
       #exit() #ne fonctionne pas
       #os._exit(0) ne fonctionne pas non plus
       sys.exit('Fin de la récupération des données') #fonctionne mais ça a l'air violent. A creuser.
   def on_error(self, status):
       print(status)

twitterStream = Stream(auth, listener(start_time, time_limit=60))
twitterStream.filter(track=keyword_list, languages=['fr'])
#twitterStream.filter(track=keyword_list, languages=['fr'])



#POUR PUBLIER SUR TWITTER - (POUR INFO SEULEMENT, INUTILE DANS NOTRE CONTEXTE)
#<status = "Testing!"
#api.update_status(status=status)