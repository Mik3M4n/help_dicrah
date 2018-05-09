# -*- coding: utf-8 -*-
"""
Created on Tue May  8 18:58:07 2018

@author: Alex
"""

import os
import json
import io

#VARIABLES GLOBALES
#Gestion des fichiers locaux
#dataFile = 'DataTweets.csv'
dataFile = 'DataTweets.csv'
dataML = 'DataML.csv'



#Définition des noms qualifiés des fichiers locaux
FQdatafile = os.getcwd() + '/' + dataFile
FQdataML = os.getcwd() + '/' + dataML


with open(FQdatafile) as f :
   for line in f :   
       if line.strip() != '':
           dico1 = json.loads(line.strip())
           #print(dico1.keys())
           TweetDate = dico1['created_at']
           #print(TweetDate)
           TweetText = dico1['text']
           print(TweetText)
           dico2 = dico1['user']
           #print(dico2.keys())
           TweetUser = dico2['screen_name']
           #print(TweetUser)
           saveFile = io.open(FQdataML, 'a', encoding='utf-8')
           TweetInfo = TweetText + ',' + TweetDate + ',' + TweetUser + '\n' 
           print(TweetInfo)
           saveFile.write(TweetInfo)
           saveFile.close()







