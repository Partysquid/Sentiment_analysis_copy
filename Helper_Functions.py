import pandas as pd
import numpy as np
import json


#Takes a json file as a string pathname
#Returns the list of the text of the tweets
#Only works on file format made by Ryan Vogt
def json_to_textlist(filepath):
    twitter_file = open(filepath, "r", encoding="utf8")
    twitter_data = []
    for line in twitter_file:
        try:
            elements = json.loads(line)
            twitter_data.append(elements['text'])
        except:
            continue


    return twitter_data

#Works better now
    

#Sees if a file exists and can be opened.
def check_file(filename):
    try:
       f = open(filename)
       f.close()
       return(True)
    except FileNotFoundError:
        return(False)

#returns true if a key is in a dict, false if not
def check_for_key(dictionary, key):
    if hasattr(dictionary, key):
        return(True)
    else:
        return(False)