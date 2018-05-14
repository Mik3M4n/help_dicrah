#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 11:56:35 2018

@author: Eduard

Ce script sert à parser les messages texte des 200 Tweets aléatoires ayant été
scrapés du compte de chaque usager dont nous avons détecté un message incorporant
l'un de nos termes cible. Ils n'incorporent pas forcément l'un des mots-cibles,
mais sont écrits par les mêmes usagers (introduction d'un dégré aléatoire).
Ils sont tous concatennés dans un fichier CSV pour lecture aisée sur Excel 
et labélisation manuelle.

"""
import json, glob, os
import pandas as pd


# On indique le chemin vers les fichiers JSON de Tweets scrappés
path = os.getcwd()+'/StreamListenerTweepy/Users/*.jsonl'


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
tweets = tweets[["retweeted_status"]]


# Extraction des index des lignes non vides et à parser
index_ret = tweets.retweeted_status[tweets.retweeted_status.notnull()].index


# Si le stream a un champ "extended_tweet" on récupère les index des ces tweets
# pour effectuer ensuite une boucle d'extraction du texte en entier.
j=[]
for i in index_ret:
    if "full_text" in tweets.retweeted_status[i]:
        j.append(i)
        
for i in j:
    tweets.retweeted_status[i] = tweets.retweeted_status[i]["full_text"]


# Enfin, on fusionne tous les tweets qui doivent être labelisées manuellement et on efface les dupliqués
tweets_dilcrah_users = tweets.stack().dropna().drop_duplicates().reset_index(drop=True)


# À cette fin, on exporte en csv pour pouvoir faire la lecture et labélisation sur Excel
tweets_dilcrah_users.to_csv('TweetsToLabelCSV/tweets_dilcrah_users.csv', sep=',', encoding='utf-8', header = False)


tweets_dilcrah_users