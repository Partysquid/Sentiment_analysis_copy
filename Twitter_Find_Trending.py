import pandas as pd
import numpy as np
from numpy import NaN
import time
from sqlalchemy import create_engine
from datetime import datetime
import sqlalchemy
import re
import Helper_Functions as HF
from sqlalchemy import text

#Program Parameters############################################################
engine = create_engine("mysql+pymysql://LOLwrite:"+
                       'LaberLabsLOLwrite'+
                       "@lolsql.stat.ncsu.edu/lol_test")
temp_df_name = "Temp_Twitter_DF.pickle"
stop_words = ["like", "is", "the", "this"]
#Functions#####################################################################

#Creation of dataframes after the inital
def create_temp_df():
   if HF.check_file(temp_df_name):
       new_temp_df = pd.read_pickle(temp_df_name)
       if new_temp_df != temp_df:
           temp_df = new_temp_df
           return new_temp_df
       else:
           return False
   else:
       return False

#Creation of the inital dataframe
def start_temp_df():
    if HF.check_file(temp_df_name):
        return pd.read_pickle(temp_df_name)
    else:
        return False
    
#see if a dict has a key
def check_for_key(dict, key):
    if hasattr(dict, key):
        return(True)
    else:
        return(False)

#Splits df into list of dataframes separated by month
def df_month_split(temp_df):
    jan_df = temp_df[temp_df['created_at']==1]
    feb_df = temp_df[temp_df['created_at']==2]
    mar_df = temp_df[temp_df['created_at']==3]
    apr_df = temp_df[temp_df['created_at']==4]
    may_df = temp_df[temp_df['created_at']==5]
    jun_df = temp_df[temp_df['created_at']==6]
    jul_df = temp_df[temp_df['created_at']==7]
    aug_df = temp_df[temp_df['created_at']==8]
    sep_df = temp_df[temp_df['created_at']==9]
    oct_df = temp_df[temp_df['created_at']==10]
    nov_df = temp_df[temp_df['created_at']==11]
    dec_df = temp_df[temp_df['created_at']==12]
    
    months_list = [jan_df, feb_df, mar_df, apr_df, may_df, jun_df, jul_df,
                   aug_df, sep_df, oct_df, nov_df, dec_df]
    return_list = []
    
    for month in months_list:
        if len(month) > 0:
            return_list.append(month)
            
    return(return_list)
#determines if a word is a stop word (commonly used english word like "is, the")
def not_stopword(word):
    for stop_word in stop_words:
        if len(word) < 2:
            return False
        if word == stop_word:
            return False
        else:
            continue
    return True

#Takes a tweet, returns a list of individual words in the tweet   
def separate_words(tweet):
    myRE = re.compile("(\w[\w']*\w|\w)", re.IGNORECASE)
    new_words = myRE.findall(tweet)
    
    return_words = []
    for word in new_words:
        word = word.lower()
        if not_stopword(word):
           return_words.extend([word]) 
    
    
    return(return_words)
#creates a dataframe of counted words for the month
def month_word_count(df):
    text_list = df['text'].values
    month = df['created_at'].values
    month = month[0]
    
    words = []
    for tweet in text_list:
        words.extend(separate_words(tweet))
    
    word_dict = dict([('word', words), ('count', 1)])
    month_df = pd.DataFrame.from_dict(word_dict)
    month_df = month_df.groupby('word', as_index = False)['count'].sum()
        
    month_df['month'] = month
    return(month_df)

def update_database(temp_df):
    split_df = df_month_split(temp_df)
    
    full_df = pd.DataFrame()
    for df in split_df:
        new_count = month_word_count(df)
        full_df = pd.concat([full_df, new_count])
    
    db_df = pd.read_sql('SELECT * from twitter_word_counts', engine)
    
    max_month = full_df['month'].max()
    min_month = full_df['month'].min()
    
    if ((max_month == 12) and (min_month == 1)):
        temp_full_df = full_df.drop(['month'] == [8,9,10,11,12])
        max_month = full_df['month'].max()
    print(max_month)
    
    full_df.to_sql(name="twitter_word_counts", con=engine, if_exists='append',
                   index=False,
                   dtype={'word': sqlalchemy.types.VARCHAR(length=100),
                          'count': sqlalchemy.types.INTEGER(),
                          'month': sqlalchemy.types.INTEGER()
                          })
                  
    return(full_df)
###############################################################################
def main():
    main_start_time = time.time()
    temp_df = start_temp_df()
    if not isinstance(temp_df, pd.DataFrame):
        print("Error, failed to find file: " + temp_df_name +
              ". Initial Dataframe did not load")
        return(1)
   
    
    full_df = update_database(temp_df)

    return(full_df)
    print("Time for 1_Twitter_Find_Trending.main(): " + str(main_start_time - 
                                                            time.time()) + "s")
    return(0)
x=main()


#TO DO
#YOULL WANT TO COUNT THEWORDS INTO A DATAFRAME, THEN JOIN THEM AND ADD THE COUNTS TO MAKE IT EASY PZ
#2. format in main function to loop through
#3. Use it to work with a database on server, and update count