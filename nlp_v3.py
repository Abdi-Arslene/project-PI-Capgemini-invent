# -*- coding: utf-8 -*-
"""NLP_v3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Oc6yKiAqapYtdbyrl_3C8TbIT1kkOK4g

# Neural Language Programming :

## Introduction :

We will now try to apply a NLP algorithm on our scrapped dataset.
First, we will try to apply a word cloud model on our dataset so that we can see visually the number of occurences 
of a word in our dataset, but only for the reviews column.
Then, after some analysis we chose to use the Topic Modelling method using the LDA Analysis algorithm which is basically a type of 
statistical language models used for uncovering hidden structures in a collection of texts.

### Project Goal :

The main goal of our project is to analyze the dataset and visualize it so that we are able to see the main features that we need through using multiple libraries and do some modelling and data pre-processing to be able to apply our NLP algorithm.

## Importing and downloading the libraries that we need :
"""

#pip install pyLDAvis

import pandas as pd
import pandas_profiling
import numpy as np

import string
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')
nltk.download('stopwords')

from wordcloud import WordCloud
import matplotlib.pyplot as plt

import gensim
from gensim.utils import simple_preprocess

import gensim.corpora as corpora


from pprint import pprint

import pyLDAvis
import pyLDAvis.gensim
import pickle 
import os



"""### Cleaning and pre-processing our dataset : """

def clean_text(text):
    # lower text
    text = text.lower()
    # tokenize text and remove puncutation
    text = [word.strip(string.punctuation) for word in text.split(" ")]
    # remove words that contain numbers
    text = [word for word in text if not any(c.isdigit() for c in word)]
    # remove stop words
    stop = stopwords.words('french')
    text = [x for x in text if x not in stop]
    # remove empty tokens
    text = [t for t in text if len(t) > 0]
    # pos tag text
    pos_tags = pos_tag(text)
    # remove words with only one letter
    text = [t for t in text if len(t) > 2]
    text = [t for t in text if t!="j'espère"]
    text = [t for t in text if t!="Length"]
    text = [t for t in text if t!="commentaire"]
    text = [t for t in text if t!="Name"]
    text = [t for t in text if t!="dtype"]
    # join all
    text = " ".join(text)
    return(text)

# Create a wordcloud image file function
def show_wordcloud(data,nom_assurance,title = None):
     w=WordCloud(
        background_color = 'white',
        max_words = 200,
        max_font_size = 40, 
        scale = 3,
        random_state = 42).generate(str(data))
     w.to_file("static/img/wordcloud/wc_"+nom_assurance+".png")


    


# Generate an image from the dataset for a single insurance
def wordcloud(nom_assurance,df):
    df_assurance = df[df["assurance"] == nom_assurance].drop(columns=['nom'], axis=1)
    df_assurance_cleaned = df_assurance["commentaire"].apply(lambda x: clean_text(x))
    show_wordcloud(df_assurance_cleaned,nom_assurance)

def words_clean(wordlist,words_to_remove):
    word_list_cleaned=[]
    for i in range(len(wordlist)):
        if wordlist[i] not in words_to_remove:
            word_list_cleaned.append(wordlist[i])
    return word_list_cleaned


# Get the words frequencies sorted
def frequencies(nom_assurance,df,words_to_remove ):
    df_assurance = df[df["assurance"] == nom_assurance].drop(columns=['nom'], axis=1)
    df_assurance_cleaned = df_assurance["commentaire"].apply(lambda x: clean_text(x))

    string=""
    for i in range(len(df_assurance_cleaned)):
        string=string+str(df_assurance_cleaned.iloc[i])+" "
    word_list_cleaned=[]
    wordlist = string.split()

    word_list_cleaned=words_clean(wordlist,words_to_remove)
    

    wordfreq = []
    for w in word_list_cleaned:
        wordfreq.append(word_list_cleaned.count(w))
    

    liste=list(zip(word_list_cleaned, wordfreq))
   
    for i in range(len(liste)):
        for j in range(i+1,len(liste)):
            if(liste[i][1]<liste[j][1]):
                aux=liste[i]
                liste[i]=liste[j]
                liste[j]=aux

    wordliste=[]
    for i in range(len(liste)):
        if(liste[i][0] not in wordliste):
            wordliste.append(liste[i][0])

    return wordliste

def sent_to_words(sentences):
    for sentence in sentences:
      	# deacc=True removes punctuations
       	yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))


def LDA(df,assurance):
	assurance_comment = df[df["assurance"] ==assurance]
	assurance_comment_clean = assurance_comment["commentaire"].apply(lambda x: clean_text(x))
	assurance_comment_clean['commentaire'] = assurance_comment["commentaire"].apply(lambda x: clean_text(x))
	assurance_comment_list = assurance_comment_clean['commentaire'].values.tolist()
	data_words_assurance = list(sent_to_words(assurance_comment_list))
	# Create Dictionary
	id2word_assurance = corpora.Dictionary(data_words_assurance)
	# Create Corpus
	texts_assurance = assurance_comment_list
	# Term Document Frequency
	corpus_assurance = [id2word_assurance.doc2bow(texts_assurance) for texts_assurance in data_words_assurance]
	# View
    # Build LDA model
    # number of topics
	num_topics = 5
	lda_model_assurance = gensim.models.LdaMulticore(corpus=corpus_assurance,id2word=id2word_assurance,num_topics=num_topics)
	# Print the Keyword in the 10 topics
	# Visualize the topics
	LDAvis_data_filepath = os.path.join('./Templates/lda/ldavis_prepared_'+assurance)
	# # this is a bit time consuming - make the if statement True
	# # if you want to execute visualization prep yourself
	if (1 == 1) :
		LDAvis_prepared = pyLDAvis.gensim.prepare(lda_model_assurance, corpus_assurance, id2word_assurance)
		with open(LDAvis_data_filepath, 'wb') as f:
			pickle.dump(LDAvis_prepared, f)
	with open(LDAvis_data_filepath, 'rb') as f:
		LDAvis_prepared = pickle.load(f)
	pyLDAvis.save_html(LDAvis_prepared, './Templates/lda/ldavis_prepared_'+assurance+'.html')


	