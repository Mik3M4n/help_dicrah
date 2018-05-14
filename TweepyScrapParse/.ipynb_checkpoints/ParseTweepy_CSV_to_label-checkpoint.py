#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 11:56:35 2018

@author: msfogg
"""
import json, glob, os
import pandas as pd

# On indique le chemin vers les fichiers JSON de Tweets scrappés
path = os.getcwd()+'/*.jsonl'
print(os.getcwd())
for filename in glob.glob(path):
    with open(filename) as json_data:
        df = pd.read_json(json_data, lines=True)
        
# On charge le JSON vers un DataFrame pandas
#df = pd.read_json(path+file, lines=True)
tweets = pd.DataFrame(df[["extended_tweet", "retweeted_status"]])


# Extraction des index des lignes non vides et à parser
index_ext = tweets.extended_tweet[tweets.extended_tweet.notnull()].index
index_ret = tweets.retweeted_status[tweets.retweeted_status.notnull()].index

# On remplace les tweets originaux et trunqués par le texte en entier
for i in index_ext:
    tweets["extended_tweet"][i] = tweets.extended_tweet[i]["full_text"]

# Pour les messages retweetés (reteewted_status) on a streamé un dict à plusiers niveaux
# Chaque json a une structure différente. Nous voulons récupérer deux champs:
# 1. les messages retweetés en entier et 2. les messages cités par le même usager

# 1. Si le stream a un champ "extended_tweet" on récupère les index des ces tweets
# pour effectuer ensuite une boucle d'extraction du texte en entier.
# Sinon (else), le message n'a pas été trunqué, on utilise le champ entier "text"
j=[]
for i in index_ret:
    if "extended_tweet" in tweets.retweeted_status[i]:
        j.append(i)
    else:
        tweets.retweeted_status[i] = tweets.retweeted_status[i]["text"]

for i in j:
    tweets.retweeted_status[i] = tweets.retweeted_status[i]["extended_tweet"]["full_text"]

# 2. Sur la même colonne d'avant on trouve le texte des messages cités par l'usager.  
# Pour ne pas l'écraser, on crée une nouvelle colonne ou l'on placera le texte en entier
k=[]
for i in index_ret:
    if "quoted_status" in df.retweeted_status[i]:
        k.append(i)
    else:
        tweets["cite_status"] = None

try:
    for i in k:
        tweets.cite_status[i] = df.retweeted_status[i]["quoted_status"]["extended_tweet"]["full_text"]
except:
    pass

# Enfin, on fusionne tous les tweets qui doivent être labelisées manuellement
tweets_dilcrah = tweets.stack().dropna().reset_index(drop=True)

# À cette fin, on exporte en csv pour pouvoir faire la lecture et labélisation sur Excel
tweets_dilcrah.to_csv('TweetsToLabelCSV/tweets_dilcrah.csv', sep=',', encoding='utf-8', header = False)

tweets_dilcrah