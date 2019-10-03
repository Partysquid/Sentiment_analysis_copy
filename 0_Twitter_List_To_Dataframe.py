import pandas as pd
import json
import numpy as np
import random

wk_dir ='C:\\Users\\Adam Durrett\\Documents\\GitHub\\sentiment_analysis\\Data\\'

#This function takes a json file name in the form of a string, and then takes the data from Ryan's twitter format
#It then formats this data into a dictionary which is then turned into a dataframe
#input: string of json filename   example: "file.json"
#output: dataframe of info from json
def json_to_table(json_filename):
    twitter_file = open(json_filename, 'r', encoding="utf8")
    twitter_data = []

    #extract json into readable format
    for line in twitter_file:
        try:
            elements = json.loads(line)
            twitter_data.append(elements)
        except:
            continue

    #declare empty dictionary to store json data
    dfDict = {}
    print(dfDict)
    #used as an index to store specific data in order
    dictIndex = 0
    #stores the tweets line by line with useful information from each of them into the dictionary
    for element in twitter_data:
        for tweet in element['tweet_list']:
            tweetDate = tweet['created_at']['$date']
            tweetTime = tweetDate[12:20]
            tweetDate = tweetDate[0:10]
            dfDict[dictIndex] = {'Name':element['name'],
                                 'Date':tweetDate,
                                 'Time':tweetTime,
                                 'Sent_Pol':tweet['sent_pol'],
                                 'Sent_Sub':tweet['sent_sub'],
                                 'Gender':tweet['gender'],
                                 'Text':tweet['text']}
            dictIndex += 1

    #create new dataframe from the json dictionary
    dfnew = pd.DataFrame.from_dict(dfDict, orient='index')
    return(dfnew)
###############################################################################

buildTable = json_to_table(wk_dir + 'Champions.json')
n_parts = 2
buildTable['Partition'] = np.random.choice(range(n_parts), len(buildTable))
print(buildTable.head(30))
buildTable.to_pickle(wk_dir + 'Champions_df.pickle')



