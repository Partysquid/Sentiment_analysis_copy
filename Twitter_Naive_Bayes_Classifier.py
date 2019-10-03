"Created by Adam Durrett"
#Naive Bayes Classifier for Twitter Data
#The purpose of this code is to create a Naive Bayes classifier that takes
#tweets with the hastags "leagueoflegends" and "riotgames" and initally trains
#off of this dataset, and then trains off of the new tweets found afterwards.
#The point is that this classifier will find the given probability that a word
#makes a tweet about league of legends, and those higher probability words can
#be used to search for new terms. Once new terms are found, we can use them to
#find new tweets using them, and continue training the classifier off of the
#tweets as they come in, allowing us to search for more recent league-based
#tweets.

#This code takes each size 100 dataframe from the API Querier, and updates the
# counts for the classifier. The classifier can then adjust itself.
import pandas as pd
import numpy as np
from numpy import NaN
import time
import sqlalchemy
from sqlalchemy import text
from sqlalchemy import create_engine
import re
import Helper_Functions as HF


#-------------------------------------------------#
# Functions #
#-------------------------------------------------#

#input: word
#output True if the word is not a stopword, False if it is.
#description: determines if a word is a stop word (commonly used english word like "is, the")
def not_stopword(word):
    for stop_word in stop_words:
        if len(word) < 2:
            return False
        if word == stop_word:
            return False
        else:
            continue
    return True

#input: tweet or sentence
#output: list of words in order as they appear in string
#description: This seperates each word in a tweet into individual parts of a
# list. Can be used to find document frequency of each word used.
def separate_words(tweet):
    myRE = re.compile("(\w[\w']*\w|\w)", re.IGNORECASE)
    new_words = myRE.findall(tweet)
    
    return_words = []
    for word in new_words:
        word = word.lower()
        if not_stopword(word):
           return_words.extend([word]) 
    return(return_words)
    
#input: list of tweets
#output: document frequency of each word in tweets. Each tweet is 1 document
#description: this breaks the list of tweets up into counts for each word, for
# how many tweets the word is included in.
def generate_word_count(tweet_list):
    word_count_dict = {}
    for tweet in tweet_list:
        word_list = seperate_words(tweet)
        temp_word_list = []
        

        
        for word in word_list:
            if word not in temp_word_list:
                temp_word_list.extend([word])
                if word not in word_count_dict:
                    word_count_dict.extend({word:1})
                else:
                    word_count_dict[word] += 1
            else:
                continue
        
        
    
#-------------------------------------------------#
def main(tweet_set_df):
    
# Program Parameters #
#-------------------------------------------------#
    engine = create_engine("mysql+pymysql://LOLwrite:"+
                       'LaberLabsLOLwrite'+
                       "@lolsql.stat.ncsu.edu/lol_test")
    stop_words = ["the", "a", "is"]
#-------------------------------------------------#
    tweet_list = tweet_set_df['text'].values
    naive_bayes_counts = pd.read_sql('SELECT * from twitter_doc_freq',engine)
    generate_word_count(tweet_list)