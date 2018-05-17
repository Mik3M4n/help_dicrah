#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 11:56:35 2018

@author: Eduard

Ce script sert à parser les messages texte des Tweets ayant été scrapés incorporant
l'un de nos termes cible. Ils sont tous concatennés dans un fichier CSV pour lecture
aisée sur Excel et labélisation manuelle.

"""
import json, glob, os
import pandas as pd


# On indique le chemin vers les fichiers JSON de Tweets scrappés
path = os.getcwd()+'/StreamListenerTweepy/Streams/*.jsonl'


# On crée deux fonctions pour itérer le parse sur plusieurs fichiers JSON 
# placés sur le même dossier
def read_json_files(path_to_file):
    with open(path_to_file) as p:
        data = pd.read_json(p, lines=True)
    return data

def giant_list(json_files):
    data_list = []
    for f in json_files:
        data_list.append(read_json_files(f))
    return data_list


# Éxecution de fonctions et chargement de JSON dans un DF concatenné
event_files = glob.glob(path)
tweets = pd.concat(giant_list(event_files), ignore_index=True)
tweets = tweets[["extended_tweet", "retweeted_status"]]
tweets_copy = tweets.copy()


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
# On l'a écrasée lors de l'opération précédente, on utilise une copie à la place.
# Pour ne pas écraser la colonne sur 'tweets', on crée une nouvelle colonne 
# ou l'on placera le texte en entier
k=[]
for i in index_ret:
    if "quoted_status" in tweets_copy.retweeted_status[i]:
        k.append(i)
    else:
        tweets["cite_status"] = None

try:
    for i in k:
        tweets.cite_status[i] = tweets_copy.retweeted_status[i]["quoted_status"]["extended_tweet"]["full_text"]
except:
    pass


# Enfin, on fusionne tous les tweets qui doivent être labelisées manuellement et on efface les dupliqués
tweets_dilcrah_keywords = tweets.stack().dropna().drop_duplicates().reset_index(drop=True)


# À cette fin, on exporte en csv pour pouvoir faire la lecture et labélisation sur Excel
tweets_dilcrah_keywords.to_csv('TweetsToLabelCSV/tweets_dilcrah_keywords.csv', sep=',', encoding='utf-8', header = False)


tweets_dilcrah_keywords