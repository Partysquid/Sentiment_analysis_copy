#Query the data with sqlalchemy + pandas
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import text
from datetime import datetime
import sqlalchemy

# this creates the connection to the DB
#engine = create_engine("mysql+pymysql://LOLwrite:"+'LaberLabsLOLwrite'+"@lolsql.stat.ncsu.edu/lol_test")

#twitter_dataframe = "Twitter_Dataframe.pickle"
#df = pd.read_pickle(twitter_dataframe)

######################################################
engine = create_engine("mysql+pymysql://LOLread:"+
                       'LaberLabsLOLquery'+
                       "@lolsql.stat.ncsu.edu/lol")
tablenames = engine.table_names()
print(tablenames)

games = pd.read_sql("SELECT * from match_list where queueid = 420 AND gameCreation > '2018-07-15 14:58:32' AND gameCreation < '2018-10-12 05:30:49'", engine)
games.to_csv("ranked_individual_games.csv")
#dictio = {"term":["#LeagueofLegends", "#RiotGames"]}
#term_df = pd.DataFrame.from_dict(dictio)

#term_df.to_sql(name= "twitter_search_terms", con=engine, if_exists='replace', index = False, dtype={'term':sqlalchemy.types.VARCHAR(length=100)})
#tweets = pd.read_sql('SELECT * from twitter',engine)

#df = df.drop_duplicates(subset = 'id',keep = "first")
#df.set_index('id')

#df['created_at'] = pd.to_datetime(df['created_at'])
#df.to_pickle(twitter_dataframe)
#print(len(tweets))
#sql = text("DELETE FROM twitter_hashtags;")
#engine.execute(sql)

#df.to_sql(name="twitter", con=engine, if_exists='replace', index=False,
#            dtype={'created_at': sqlalchemy.DateTime(), 
#                  'favorite_count':  sqlalchemy.types.INTEGER(),
#                   'hashtags': sqlalchemy.types.VARCHAR(length=200),
#                   'id': sqlalchemy.types.BIGINT(),
#                   'is_retweet': sqlalchemy.types.Boolean,
#                   'lang':sqlalchemy.types.VARCHAR(length=3),
#                   'location':sqlalchemy.types.VARCHAR(length=100),
#                   'original_id':sqlalchemy.types.BIGINT(),
#                   'retweet_count': sqlalchemy.types.INTEGER(),
#                   'search_term': sqlalchemy.types.VARCHAR(length=100),
#                   'text': sqlalchemy.types.Text,
#                   'truncated': sqlalchemy.types.Boolean,
#                   'user_id': sqlalchemy.types.BIGINT(),
#                   'username': sqlalchemy.types.VARCHAR(length=100)
#                   })
#df['is_retweet'] = 

#hashtags = pd.read_sql('SELECT * from twitter_word_counts', engine)

#tweets = pd.read_sql('SELECT * from twitter', engine)

#Fix the is_retweet column, kinda broken

#test = select([twitter])
#result = engine.execute(test)

"SELECT Color, Month, SUM(number) as number FROM Twitter_words_table GROUP BY Color, Month;"