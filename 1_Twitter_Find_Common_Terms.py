import pandas as pd
import numpy as np
from numpy import NaN
import time
import Helper_Functions
from collections import Counter
from sqlalchemy import create_engine
#Program Parameters ###########################################################
engine = create_engine("mysql+pymysql://LOLwrite:"+
                       'LaberLabsLOLwrite'+
                       "@lolsql.stat.ncsu.edu/lol_test")
twitter_df = pd.read_sql('SELECT * from twitter', engine)

#Functions ####################################################################
def create_df():
    if Helper_Functions.check_file(twitter_dataframe):
        return(pd.read_pickle(twitter_dataframe))
    else:
        quit()
            
      
#Main Function ################################################################
#finds top hashtags with Retweets excluded
def fun_find_hashtags_NORTs():
    start_time = time.time()# .011s
    twitter_df = create_df() 
    twitter_df = twitter_df.drop_duplicates(subset = 'text', keep = "first")
    top_hashtags = {}
    hashtags_list = twitter_df['hashtags'].values
    date_list = twitter_df['created_at'].values
    
    i = 0 #index value
    for hashtags in hashtags_list:
        date = date_list[i][0:10]
        for tag in hashtags:
            text = tag.text
            if date in top_hashtags:
                if text in top_hashtags[date]:
                    top_hashtags[date][text] += 1
                else:
                    top_hashtags[date][text] = 1
            else:
                top_hashtags[date] = {text:1}
        
        i += 1
    print("Time for fun_find_hashtags_NORTs: " + str(time.time()-start_time))
    return(top_hashtags)

#finds top hashtags with Retweets included
def fun_find_hashtags_WRTs():
    start_time = time.time() # .005s
    twitter_df = create_df() 
    top_hashtags = {}
    hashtags_list = twitter_df['hashtags'].values
    date_list = twitter_df['created_at'].values
    
    i = 0 #index value
    for hashtags in hashtags_list:
        date = date_list[i][0:10]
        for tag in hashtags:
            text = tag.text
            if date in top_hashtags:
                if text in top_hashtags[date]:
                    top_hashtags[date][text] += 1
                else:
                    top_hashtags[date][text] = 1
            else:
                top_hashtags[date] = {text:1}
        
        i += 1
    print("Time for fun_find_hashtags_WRTs: " + str(time.time()-start_time))
    return(top_hashtags)
    
#This function counts the amont of times any individual word is used in all
# tweets, excluding all retweets   
def fun_find_topwords_NORTs():
    start_time = time.time()
    twitter_df = create_df() 
    twitter_df = twitter_df.drop_duplicates(subset = 'text', keep = "first")
    
    tweets_list = list(twitter_df['text'].values)
    all_tweets = []
    for tweet in tweets_list:
        split_tweet = tweet.split()
        all_tweets = all_tweets + split_tweet
    
    count = Counter(all_tweets)
    print(count)
    return(count)

#This function counts the amont of times any individual word is used in all
# tweets, with the addition of retweets
def fun_find_topwords_WRTs():
    start_time = time.time()
    twitter_df = create_df() 
    
    tweets_list = list(twitter_df['text'].values)
    all_tweets = []
    for tweet in tweets_list:
        split_tweet = tweet.split()
        all_tweets = all_tweets + split_tweet
    
    count = Counter(all_tweets)
    print(count)
    return(count)

hashtags_no_rts = fun_find_hashtags_NORTs()

hashtags_with_rts = fun_find_hashtags_WRTs()

topwords_no_rts = fun_find_topwords_NORTs()

topwords_with_rts = fun_find_topwords_WRTs()

#Date is created_at[0:10]