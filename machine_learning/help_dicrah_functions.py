import unidecode
from nltk.tokenize import WordPunctTokenizer
from bs4 import BeautifulSoup
import re
from  nltk.stem.snowball import FrenchStemmer, EnglishStemmer
import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns










def tweet_cleaner(text, my_dict):
        
    # fixes encoding problem (MICHELE)
    if type(text)!=unicode and type(text)!=float:
        try: 
            text= unicode(text,'utf-8')
        except UnicodeDecodeError: 
            text= unicode(text,'latin-1')
    if type(text)==float:
        text = str(text)
    
    tok = WordPunctTokenizer()

    pat1 = r'@[A-Za-z0-9_]+'
    pat2 = r'https?://[^ ]+'
    combined_pat = r'|'.join((pat1, pat2))
    www_pat = r'www.[^ ]+'
    rt_path = r'^rt'
    paths =  [combined_pat, www_pat,rt_path ]
    
        
    text = unidecode.unidecode(text)
    soup = BeautifulSoup(text, 'lxml')
    souped = soup.get_text()
    
    for word in my_dict:
        souped = re.sub(word, my_dict[word], souped)
    
    try:
        bom_removed = souped.decode("utf-8-sig").replace(u"\ufffd", "?")
    except:
        bom_removed = souped
    
    for path in paths:
        bom_removed = re.sub(path, '', bom_removed.lower())
    
    letters_only = re.sub("[^a-zA-Z]", " ", bom_removed)
    
 
    # During the letters_only process two lines above, it has created unnecessay white spaces,
    # I will tokenize and join together to remove unneccessary white spaces
    words = [x for x  in tok.tokenize(letters_only) if len(x) >= 1]
    return (" ".join(words)).strip()


def tokenize(text, stem=False):
    tweet = " ".join(re.split("[^a-zA-Z]*", text.lower())).strip()
    if stem:
        stemmer = FrenchStemmer()
        tokens = [stemmer.stem(t) for t in tweet.split() if len(stemmer.stem(t))>2 ]
    tokens = tweet.split(' ')
    return tokens



def generate_stopwords():
    stopwords_en = nltk.corpus.stopwords.words("english")
    stopwords_fr = nltk.corpus.stopwords.words("french")
    stop_words = stopwords_en+stopwords_fr
    #other_exclusions = ["#ff", "ff", "rt"]
    #stop_words.extend(other_exclusions)
    return stop_words

def remove_stopwords(text_list, sw):
    return [word for word in text_list if word not in sw]


my_dict={"aujourd'hui":"aujourdhui", "s'il":"si il", "s'":"se ","n'":"ne ", 'jte':"je te", 'pck':'parce que', 'jms':'jamais',
        'fdp': 'fis de pute', 'ptn': 'putaine', 'pcq':'parce que', 'tt ': 'toute', 'vrmt': 'vraiment',
         "m'a'": 'me a','ptdr':" plie tordu de rire", "c'est":"ce est","m'":"me ", "jrnee":"jourrnee",'pxtain': 'putaine', 'bz':'baisez'}




def add_lexical_features(df):
    urls = re.compile(r"http")
    ats = re.compile(r"@[a-zA-Z.]*")
    hashtags = re.compile(r"#[a-zA-Z]*")
    letters = re.compile(r"[a-zA-Z]")
    caps = re.compile(r"[A-Z]")
    fancy = [";",'\"','(','<<']

    nbr_characters = [len(s) for s in df.Texte]
    df['nbr_characters'] = pd.DataFrame(nbr_characters, index=df.index)

    nbr_words = [len(s.split()) for s in df.Texte] # to update after cleaning
    df['nbr_words'] = pd.Series(nbr_words, index=df.index)

    nbr_ats = [len(ats.findall(text)) for text in df.Texte]
    df['nbr_ats'] = pd.Series(nbr_ats, index=df.index)

    nbr_hashtags = [len(hashtags.findall(text)) for text in df.Texte]
    df['nbr_hashtags'] = pd.Series(nbr_hashtags, index=df.index)

    nbr_urls = [len(urls.findall(text)) for text in df.Texte]
    df['nbr_urls'] = pd.Series(nbr_urls, index=df.index)

    nbr_letters = [len(letters.findall(text)) for text in df.Texte]
    df['nbr_letters'] = pd.Series(nbr_letters, index=df.index)

    nbr_caps = [len(caps.findall(text)) for text in df.Texte]
    df['nbr_caps'] = pd.Series(nbr_caps, index=df.index)

    nbr_fancy = [sum(1 for c in text if c in fancy) for text in df.Texte]
    df['nbr_fancy'] = pd.Series(nbr_fancy, index=df.index)

    return df
 






def print_cm(y_test,y_preds, names):

    from sklearn.metrics import confusion_matrix
    confusion_matrix = confusion_matrix(y_test,y_preds)
    matrix_proportions = np.zeros((len(names),len(names)))
    for i in range(0,len(names)):
        matrix_proportions[i,:] = confusion_matrix[i,:]/float(confusion_matrix[i,:].sum())

    confusion_df = pd.DataFrame(matrix_proportions, 
                            index=names,columns=names)
    plt.figure(figsize=(5,5))
    sns.heatmap(confusion_df,annot=True,
            annot_kws={"size": 12},cmap='gist_gray_r',
            cbar=False, square=True,fmt='.2f');
    plt.ylabel(r'True categories',fontsize=14);
    plt.xlabel(r'Predicted categories',fontsize=14);
    plt.tick_params(labelsize=12);
    plt.show()
    
    return confusion_matrix






class TfidfEmbeddingVectorizer(object):
    
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.word2weight = None
        self.dim = len(word2vec.itervalues().next())

    def fit(self, X):
        tfidf = TfidfVectorizer()
        tfidf.fit(X)
        # if a word was never seen - it must be at least as infrequent
        # as any of the known words - so the default idf is the max of 
        # known idf's
        max_idf = max(tfidf.idf_)
        print(max_idf)
        self.word2weight = defaultdict(
            lambda: max_idf,
            [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])

        return self

    def transform(self, X):
        return np.array([
                np.mean([self.word2vec[w] * self.word2weight[w]
                         for w in words.split(' ') if w in self.word2vec] or
                        [np.zeros(self.dim)], axis=0)
                for words in X
            ])





def get_tfidf_frequencies(data):

    # Note: Equivalent to CountVectorizer followed by TfidfTransformer
    tfidf = TfidfVectorizer(sublinear_tf=True, 
                            tokenizer=lambda x: tokenize(x, stem=False),
                            preprocessor=lambda x: tweet_cleaner(x, my_dict),
                            ngram_range=(1, 3),
                            use_idf=True,
                            smooth_idf=False,
                            norm=None,
                            decode_error='replace',
                            max_features=10000,
                            min_df=5,
                            max_df=0.75,
                            stop_words=generate_stopwords())

    features = tfidf.fit_transform(data).toarray()
    sum_words = features.sum(axis=0)
    words_freq ={word: sum_words[idx] for word,idx in tfidf.vocabulary_.items()}
    vocab = {v:i for i, v in enumerate(tfidf.get_feature_names())}

    return features, words_freq, vocab
