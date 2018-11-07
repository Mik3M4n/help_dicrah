# Help_dilcrah: a hate speech detection tool on Twitter (in French)

Hate speech detection on social networks is a widely studied problem at the intersection of different domains. It can be approached from multiple point of views, such as linguistical, political, sociological, and so on. It is also an interesting Machine Learning problem. 
Recently, the French governmental agency DILCRAH (Délégation Interministérielle à la Lutte Contre le Racisme, l'Antisémitisme et la Haine anti-LGBT) launched a [plan](https://www.gouvernement.fr/plan-national-de-lutte-contre-le-racisme-et-l-antisemitisme-2018-2020) to fight racism, with a focus on social networks. Having being released more or less at the same time as our Data Science intensive program happened, we thought we could take inspiration for our final project and contribute with our work to the public interest. So we decided to develop a **supervised classifier for hate speech detection on Twitter in French**.

While a good amount of related work exists in English, we are not yet aware of anything similar in French, so we had to actually face the entire pipeline of an actual Data Science problem from finding the data to the final release of the code. 
The final goal was to train a classifier that could be integrated in the Twitter API to detect hate speech during a Twitter stream.

So, the problem can be divided in three steps:

 *  Obtaining a dataset (relative code and docs in the folders tweet_listener and tweet_parser)
 * Develop and train a ML algorithm (folder machine_learning)
 * Integrate in the twitter API (folder tweet_listener)

Being our project limited to less than two months, we shall not provide the definitive dataset or classifier here: as we will see, the data and models can and should be improced for a variety of reasons that we will explain. However, all the tools to expand our base model are available and documented and **we provide a complete pipeline, from data collection to the final product: an online tool to detect hate speech during a Twitter stream**.

The docs for the different parts of this project can be found in the relative folders.



## Obtaining a dataset

We aim to develop a classifier to label racist, homophobic, or generally speaking "hateful" contents on Twitter. 

**The first problem is then to get a raw dataset to classify**. Of course, classifying "racist" or "hateful" contents is a delicate task due to several factors, such as possible differences in the interpretation of the defitions themselves (and the correlation between these differences and bias factors such as social status, gender, race, and so on), or the way data are collected. Here we discuss some of these issues, even if the goal of this post is not to give an exaustive discussion of these problems.

So, the question: "How do we collect a good dataset?" is all but trivial. A good starting point would have been to find some collection of tweets already signaled to the French government, but we couldn't find any (and still, notice that this would raise potential strong problems of *bias*: who contacts the police? Why? Is there a balance between, say black and white people? All this information is not available to us). 
So, we had to find our data from scratch. We decided to launch a query with the twitter api to look for tweets containing a set of words that might be associate with racist content ([See here](https://arxiv.org/abs/1703.04009)).  We compiled the list by combining a translation in French of the [Hatebase.org lexicon](https://www.hatebase.org/) (filtered to keep only expressions that make sense in French), and a list of words automatically banned from the Android dictionary. The list obtained this way is available in the file tweet_listener/query_words.txt
 
We also thought that, especally with a small dataset and with little time to collect tweets, this choice could lead to a strong bias in the data - at the end, all the tweets contain at least a word from our starting lexicon, so we could have been simply "suggesting" to the algorithm what to look for. 
A way to go around this problem could be to collect a large amounts of tweets for a long period of time, and then work only on a randomly selected subsample, large enough to be various in lexical features. This is also a good way to avoid another bias due to the structure of twitter, that is strongly related to hashtags and trending topics. In our case, we couldn't afford such a long procedure due to our time limitations.
So, we came up with a second way to collect data, namely, **we launched a query that searched from specifis terms in replies** to tweets, such as "racist", "homophobic" etc. , with the idea that these replies might be addressed to "suspect" tweets (Of the type "@someone: what you said is definitely racist!"). Then, our code fetched the entire conversation with a recursive call. 

![get_all_replies](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/get_all_replies.png) 

The query can be launched using the code stream_listener.py in the folder tweet_listener. 

At the end, we collected a dataset of 4000 tweets of which around half come from direct search using the lexicon, and the remaining part is obtained looking at replies. Of course the dataset is too litle to develop a great classifier, but we had to face severe time constraints. We shall comment on this later.
 The data collected this way consist in a .jsonl file (link) where each line represent a tweet in .json format. All the information avaliable is described in the [twitter documentation](https://developer.twitter.com/en/docs.html).
The raw data was parsed using the scripts provided in the folder tweet_parser to obtain a .csv file. 

Next step was to get a labeled dataset. The definition of concepts such as "racist", "homophobic", "violent" can be very subjective. The initial goal was to develop a multi-class classfier to predict if a tweet lies in one of the three categories: 1-Racist/is homophobic, 2-Violent but not explicitly racist, 3-Neutral. We chose to adopt the definition used in [this work](http://www.aclweb.org/anthology/N16-2013). The labelisation procedure is probably the most exposed to problems of bias. A good procedure would be to have each tweet labeled by at least three different persons, and finally assign the label by majority vote. We initially tried this strategy, but since we cannot afford crowdsourcing (if it exists in French !) and tagging was too time consuming, we finally just labeled the tweets trying to stick as much as possible to the initial definition. We also restricted the classes from three to two: Violent/Racist and Neutral. The code can however be easily extended to the multi-class case. 

The labeled dataset is available in the folder /data.

 
## Classifier

In this section we describe our classifier.

### Pre-processing and features
We tried several different ways to build features.
First, the tweets are always pre-processed by 
- lowercasing
- removing punctuation and numbers
- removing urls (but N. of urls used as feature) (con be improved, e.g. keep only main url part, for example name of the site)
- removing mentions
- removing hashtags (but n. of ht used as feature) (can be improved, e.g. use hashtag as features )
- removing special characters and smileys (can be improved, e.g. smileys can proxy sentiment)

Then, we tried two different approaches:
 
-  not stemming and keeping stopwords
 
-  stemming and removing stopwords

This choice is motivated by the fact that we wanted to ascertain whether removing stopwords and stemming influences the features by changing the context of a word. For example, the expression "I'm not racist, but...", often associated with racist content, would become just "racist" after removing stopwords. An example is given below.

![stemming](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/stemming.png) 



We tried to build features in several ways: 

- TF-IFD vectorizer with n-gram features ($ 1<=n<=3 $), fitted on the labeled dataset. We shall refer to these as "TF-IDF" features. The features dimensions are set to 90% the size of the dataset, to reduce overfitting. 

- Word-to-vec (w2v) vectorizer fitted on an unlabeled dataset of 1 milion tweets. This vectorizer maps each word into an n-dimensional feature vector. We choose $n=300$. Then, to build features, we average the word vectors of all words in a tweet. We shall refer to these as "unweighted" features

- w2v vectorizer fitted on an unlabeled dataset of 1 milion tweets. This time, before averaging, we weight each word vector with its TF-IDF weight. We shall refer to these as "weighted" features. Not that this require a somewhat longer computation time
Reference: http://nadbordrozd.github.io/blog/2016/05/20/text-classification-with-word2vec/

- Finally, we tried to re-train the w2v vectorizer on a subsample of the original 1-milion-long dataset. The subsample is selected by computing the 'similarity' between the average vector of the labeled dataset, and the features of the unlabeled dataset. The similarity is defined as the cosine between the two vectors in the features' space. The subsample is selected setting a threshold similarity of 0.5 and keeping only tweets more than 5 words long. 


We train classifiers for the four set of features above. For each of the one, we try different algorthms: Logistic Regression, SVM, and Random Forest. We run a grid parameter search and maximize the recall in the "positive" class (i.e., the class labeled as "Hateful" or "Racist"). This choice is motivated by two facts:

- the two classes are highly umbalanced with a large majority of the tweets being "Neutral"
- if the goal is to detect and signal a racist tweet, we thought that predicting a racist tweet as "Neutral" is a worst case than its opposite (signaling a tweet that is actually neutral - we assume that ultimately the tweets labeled as "H" or "N" are reviewed by humans). 

So, we minimize the false negative rate. 
The ipython notebook to train models is in the folder machine_learning. For reasons of storage, we don't provide the models here, but we are happy to provide them on demand.

Here we show results for features obtained by stemming and removing stopwords.
We also tried using features without stemming and keeping stopwords, but this results in an overall worse performance. So we show results only for the best case.

### Results

#### 1. TFIDF
![tfidf](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/tfidf.png) 

#### 2. Unweighted w2v
![unweighted_w2v](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/unweighted_w2v.png) 

#### 3. Weighted w2v, full dataset
![weighted_w2v](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/weighted_w2v.png) 

#### 4. Weighted w2v, selected dataset
![weighted_w2v_selected](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/weighted_w2v_selected.png) 

#### 5. Undersampling
Finally, as the two label classes were highly unbalanced, we tried to train the classifier on a balanced sample. This is done with a random undersampling. The resulting dataset is small (544 tweets in each class)

![Undersampling](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/undersampling.png) 



### Conclusions: best model 

As for the w2v features, in general, the weighted scheme seem to perform better than the unweighted. So, the higher evaluation time is worth. 
Also, w2v does significantly better than Tf-Idf alone.
On the other hand, it is not completely clear if using selected features gives better performance.

Conclusion: the best model is a Logistic Regression with l1 reg. and C=1 .
It seem to work (slightly) better with  w2v trained on the full sample rather than on the selected sample (why? Because the selected sample it's trained with less data? ). However, the difference is tiny and more investigation seems important (e.g. cross-validation).

If we use a Tf-Idf vectorizer, we get that the best classifier is a Random Forest with gini criterion. This does considerably worse that w2v+log reg if we consider the False positive rate (predicted =N but true=H ), and better if we consider the false negative (predicted=H but true=N). 
Since it's better to minimize false positive rate, we conclude that w2v works better.  

Finally, using undersampling techniques may improve the performace, in particular on the false positive rate, even if the size of the dataset is highly reduced. Given the small amount of data available, however, this risks to worsen the classifier's performance when applied to previously unseen data, and also the performance can fluctuate considerably when changing subsampling. However, this result is interesting to keep in mind if one has a larger dataset.



## Using the twitter API
The best model can be integrated in the stream. We mad this option available in the code stream_listener.py . Refer to the docs in the folder tweet_listener for usage. 

![Sentiment](https://github.com/Mik3M4n/help_dicrah/tree/master/pics/predict_sentiment.png) 

In this base version, the code prints an alert on standard output and saves tweets with the corresponding prediction. It can easily be extended to more complex tasks (e.g. automatically replying).





 
 
