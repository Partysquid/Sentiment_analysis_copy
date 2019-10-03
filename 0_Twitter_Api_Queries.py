import pandas as pd
import numpy as np
from numpy import NaN
import time
import twitter
from sqlalchemy import create_engine
import sqlalchemy
from multiprocessing import Pool
import Twitter_Find_Trending as FT

#Setting up Twitter
api = twitter.Api(
        consumer_key='9DKs9aNmQ8hOPinha19B2il8D',
        consumer_secret='wMJusrcalGHTgwvti0WOVOJOaSZLsC6CR0V4wlGscSdnAHsRvY',
        access_token_key='1004739347764203520-1EzcMfCQRpU51b621FCL2PiYRro3rt',
        access_token_secret='9nA8dDg1QBfHG1SLDfzdPsNqT8H4kBx3k6P2eVIPeuit0',
        sleep_on_rate_limit = True
        )
#Program Parameters############################################################

df_name = "Twitter_Dataframe.pickle"
engine = create_engine("mysql+pymysql://LOLwrite:"+
                       'LaberLabsLOLwrite'+
                       "@lolsql.stat.ncsu.edu/lol_test")
pool = Pool()
iterations = 0
errors = 0
#Functions#####################################################################

#returns True if file exists, False otherwise
def check_file(filename):
    try:
       f = open(filename)
       f.close()
       return(True)
    except FileNotFoundError:
        return(False)
        
def try_connect():
    try:
        f = pd.read_sql('SELECT * from twitter Limit 1', engine)
        return(True)
    except FileNotFoundError:
        return(False)

#loads dataframe of data, or creates new one if it doesnt exist
def init_df(filename):
    start_time = time.time()
    if try_connect():
        df = pd.read_sql('SELECT * from twitter', engine)
        print("Time for init_df(): " + str(time.time()-start_time) + "s")
        return(df)
    else:
        new_dataframe = pd.DataFrame(columns= ["created_at", "favorite_count",
                                      "hashtags", "id", "lang",
                                      "retweet_count", "text", "truncated",
                                      "username","user_id",
                                      "location", "search_term",
                                      "is_retweet", "original_id"])
        new_dataframe.to_pickle(filename)
        print("Time for init_df(): " + str(time.time() - start_time) + "s")
        return new_dataframe

#creates an empty dictionary to be created in the same format as the dataframe
def create_empty_dict(len_search):
    empty_dict = {"created_at": list(np.zeros(len_search)), 
                  "favorite_count": list(np.zeros(len_search)), 
                  "hashtags": list(np.zeros(len_search)),
                  "id": list(np.zeros(len_search)),
                  "lang": list(np.zeros(len_search)),
                  "retweet_count": list(np.zeros(len_search)),
                  "text": list(np.zeros(len_search)),
                  "truncated": list(np.zeros(len_search)), 
                  "username": list(np.zeros(len_search)), 
                  "user_id": list(np.zeros(len_search)),
                  "location": list(np.zeros(len_search)),
                  "search_term": list(np.zeros(len_search)),
                  "is_retweet": list(np.zeros(len_search)),
                  "original_id": list(np.zeros(len_search))
                  }
    return(empty_dict)

#checks if a key is in a dict
def check_for_key(search_result, key):
    if hasattr(search_result, key):
        return(True)
    else:
        return(False)

#Finds the ID of the original tweet, doesn't seem to always work though?
def find_retweet_ID(result):
    if check_for_key(result, "retweeted_status"):
        if check_for_key(result.retweeted_status, "id"):
            return(result.retweeted_status.id)
        else:
            return(NaN)
    else:
        return(NaN)
    
#Turns search result into a small dataframe with info needed
#Input: Search Result, search term
#Output: Dataframe of search result
def convert_search_to_df(search, word):
    start_time = time.time()
    index = 0
    len_search = len(search)
    search_dict = create_empty_dict(len_search)
    print(word)
    for result in search:
        search_dict["created_at"][index] = result.created_at
        search_dict["favorite_count"][index] = result.favorite_count
        search_dict["hashtags"][index] = result.hashtags
        search_dict["id"][index] = result.id
        search_dict["lang"][index] = result.lang
        search_dict["retweet_count"][index] = result.retweet_count
        search_dict["text"][index] = result.text
        search_dict["truncated"][index] = result.truncated
        search_dict["username"][index] = result.user.name
        search_dict["user_id"][index] = result.user.id
        search_dict["location"][index] = result.user.location
        search_dict["search_term"][index] = word
        search_dict["original_id"][index] = find_retweet_ID(result)
        
        if search_dict["original_id"][index] == True:
            search_dict["is_retweet"][index] = check_for_key(result,
                       "retweeted_status")
        else:
            search_dict["is_retweet"][index] = False
        index += 1

    search_df = pd.DataFrame.from_dict(search_dict)
    print("Time for convert_search_to_df(): "+str(time.time()-start_time)+"s")
    return(search_df)
    
#Searches for a search term, based on word provided and max ID
#Inputs: Search term, Max ID
#Output: Dataframe of searches based off word and max ID
def search_for_word(word, maxID):
    start_time = time.time()
    search = api.GetSearch(term = word, max_id= maxID, count = 100)
    search = convert_search_to_df(search, word)
    print("Time for search_for_word(): " + str(time.time()-start_time) + "s")
    return(search)
    
#Begins the process of searching for tweets based off the keyword
#Inputs: Keyword/searchterm, dataframe of data from that search term
#Output: Completed search dataframe of keyword
def initialize_search(word, term_dataframe):
    start_time = time.time()
    original_term_df = term_dataframe
    if len(term_dataframe) > 0:
        current_search = search_for_word(word, False)
        
        tweet_matches_old = 0
        
        while tweet_matches_old == 0:
            
            compared_dfs = current_search['id'].isin(term_dataframe['id'])
            current_search_ids = current_search['id'].values
            term_ids = term_dataframe['id'].values
            any_match = lambda current_search_ids, term_ids: any(i in term_ids for i in current_search_ids)
            
            
            if any_match:
                term_dataframe = pd.concat([term_dataframe, current_search],
                                           sort = True)
                term_dataframe = term_dataframe.drop_duplicates(subset = 'id',
                                                                keep = "first")
                tweet_matches_old = 1
            else:
                term_dataframe = pd.concat([term_dataframe, current_search])
                minID = current_search['id'].min() - 1
                current_search = search_for_word(word, minID)
                if current_search == False:
                    print("Done Searching For: " + word + "\n")
                    term_dataframe = pd.concat([term_dataframe, current_search])
                    print("Time for initialize_search(): " +
                          str(time.time()-start_time) + "s")
                    term_dataframe = pd.concat([term_dataframe,
                                                original_term_df]).drop_duplicates(keep=False)
                    return(term_dataframe)
    else:
        current_search = search_for_word(word, False)
        while not current_search.empty:
            term_dataframe = pd.concat([term_dataframe, current_search])
            minID = current_search['id'].min() - 1
            current_search = search_for_word(word, minID)
    print("Time for initialize_search(): " + str(time.time()-start_time) + "s")
    term_dataframe = pd.concat([term_dataframe, original_term_df],
                               sort = True).drop_duplicates(subset = 'id',
                                          keep=False)
    return(term_dataframe)
    
#Converts the hashtags into a comma seperated string
    #Apply to df
def replace_hashtags(list_of_tags):
    new_format = ''
    for tag in list_of_tags:
        new_format = new_format + str(tag.text) + ','
    return(new_format[0:-1])

#Formats the search_df before being uploaded to sql db
#Inputs: Search_df, keyword used to search
#Output: search_df with removed searches that dont have keyword in text or
    #hashtags, and hashtags column is turned into comma-seperated string
def final_cleanup(search_df, word):
    search_df['hashtags'] = search_df['hashtags'].apply(replace_hashtags)
    search_df.set_index('id')
    search_df['created_at'] = pd.to_datetime(search_df['created_at'])
    return(search_df)
    
def explode(df, lst_cols, fill_value=''):
    # make sure `lst_cols` is a list
    if lst_cols and not isinstance(lst_cols, list):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)

    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()

    if (lens > 0).all():
        # ALL lists in cells aren't empty
        return pd.DataFrame({
            col:np.repeat(df[col].values, lens)
            for col in idx_cols
        }).assign(**{col:np.concatenate(df[col].values) for col in lst_cols}) \
          .loc[:, df.columns]
    else:
        # at least one list in cells is empty
        return pd.DataFrame({
            col:np.repeat(df[col].values, lens)
            for col in idx_cols
        }).assign(**{col:np.concatenate(df[col].values) for col in lst_cols}) \
          .append(df.loc[lens==0, idx_cols]).fillna(fill_value) \
          .loc[:, df.columns]
#Main Function#################################################################
def main_func():
    trending_temp_dataframe = pd.DataFrame()
    twitter_dataframe = init_df(df_name)
    while True:
        search_terms_df = pd.read_sql('SELECT * from twitter_search_terms', engine)
        search_terms = list(search_terms_df['term'].values)
        for word in search_terms:                
            term_dataframe = twitter_dataframe[twitter_dataframe['search_term']==word].copy()
            search_df = initialize_search(word, term_dataframe)
            
            #convert hashtags to comma-seperated string
            search_df = final_cleanup(search_df, word)
            
            #make a new df to upload to hashtags table
            if not search_df.empty:
                hashtag_df = search_df[['id', 'hashtags', 'text', 'created_at']]
                hashtag_df = explode(
                        hashtag_df.assign(hashtags=
                                          hashtag_df.hashtags.str.split(',')),
                                          'hashtags')
                
                temp_addition = hashtag_df
                temp_addition['created_at'] = temp_addition['created_at'].dt.month
                trending_temp_dataframe = pd.concat([trending_temp_dataframe,
                                                     temp_addition],
                                                     sort = True)
                trending_temp_dataframe.to_pickle("Temp_Twitter_DF.pickle")
                if len(trending_temp_dataframe) > 10000:
                    if iterations > 0:
                        errors += result1.get(timeout = 240)
                    result1 = pool.apply_async([FT.main])
                    trending_temp_dataframe = pd.DataFrame()
                    trending_temp_dataframe.to_pickle("Temp_Twitter_DF.pickle")
                    iterations += 1
                
                hashtag_df_final = hashtag_df[['id','hashtags']]
                hashtag_df_final.to_sql(name="twitter_hashtags", con=engine,
                                 if_exists='append', index=False,
                    dtype={'id': sqlalchemy.types.BIGINT(),
                   'hashtags': sqlalchemy.types.VARCHAR(length=200)
                   })
                
                
            search_df = search_df.drop(['hashtags'], axis = 1)
            
            #add searches to sql database
            search_df.to_sql(name="twitter", con=engine, if_exists='append',
                             index=False,
                    dtype={'created_at': sqlalchemy.DateTime(), 
                   'favorite_count': sqlalchemy.types.INTEGER(),
                   'id': sqlalchemy.types.BIGINT(),
                   'is_retweet': sqlalchemy.types.Boolean,
                   'lang': sqlalchemy.types.VARCHAR(length=3),
                   'location': sqlalchemy.types.VARCHAR(length=100),
                   'original_id': sqlalchemy.types.BIGINT(),
                   'retweet_count': sqlalchemy.types.INTEGER(),
                   'search_term': sqlalchemy.types.VARCHAR(length=100),
                   'text': sqlalchemy.types.Text,
                   'truncated': sqlalchemy.types.Boolean,
                   'user_id': sqlalchemy.types.BIGINT(),
                   'username': sqlalchemy.types.VARCHAR(length=100)
                   })
            
            
            twitter_dataframe = pd.concat([search_df, twitter_dataframe], sort = True)
            twitter_dataframe = twitter_dataframe.drop_duplicates(subset = 'id',
                                                          keep = "first")
            twitter_dataframe.to_pickle(df_name)
    
main_func()
###Notes:
    #create searches based off min id in dataframe, based off search term
    #twitter_dataframe.loc(twitter_dataframe['search_term']==word).copy()