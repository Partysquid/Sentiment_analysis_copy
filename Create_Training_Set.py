import pandas as pd
import numpy as np
import json
import random
import pickle

Champion_name = "Kha'Zix" #change this to whatever champion you are working on
#if there is an error it means you either spelled the name wrong or did not capitalize correctly
Partition_number = 0 #change this to whatever partition you are working on 0 or 1 only
#if there is an error it means you used a partition that is not 1 or 0

#in the list of scores, the first index represents the current index you are working on.
#The list of scores index corresponds with the tweets list index +1

#/////Program Parameters/////#
wk_dir =''
number_classifying = 1000
data_set = pd.read_pickle(wk_dir + 'Champions_df.pickle')
instructions = open("instructions.txt", "r")
instructions = instructions.read()
save_filename = Champion_name + '_' + str(Partition_number) + '.json'
champion_tweet_list_filename = Champion_name +"_tweets" + "_" + str(Partition_number) + ".json"
scored_list = []

#Functions##############################
#Input: Dataset, champion name, part
#Output: List of text from dataset of the champion name given and partition

#turns the selected dataframe's text into a list of tweets
def dataset_tolist(df):
    return(list(df[(df['Partition'] == Partition_number) & (df['Name'] == Champion_name)]['Text'].values))

#Selects dataframe based on champion and partition picked
def select_df():
    df = data_set[(data_set['Partition'] == Partition_number) & (data_set['Name'] == Champion_name)].copy()
    df_classifying = df.sample(n=number_classifying)
    return(df_classifying)

#Tests if file exists, and is writable or readable
def file_exists(filename, method):
    try:
        f = open(filename, method)
        f.close()
    except FileNotFoundError:
        return False
    return True

#Main Function#////////////////////////////////////////////////////////////////////////////////////////////////////////

print(instructions)
agreement = input("\nType 'yes' if you understand: ")

if agreement != 'yes':
    print('Email me at aldurret@ncsu.edu or message me on slack @Adam Durrett(Partysquid) if you have any questions.')
    quit()

#checking if user has already randomly generated a text list
if file_exists(champion_tweet_list_filename, "r"):
#if they have build it from the savefile
    with open(champion_tweet_list_filename, "r", encoding="utf8") as champion_tweets:
        data_list = []
        for line in champion_tweets:
            data_list.append(line.strip())
#if they haven't create it based on selected champion and partition
else:
    current_data = select_df()
    data_list = dataset_tolist(current_data)


#checking if user identified list is available
if file_exists(save_filename, "r"):
#if they have build it from the savefile
    save_file = open(save_filename, "r")
    for line in save_file:
        scored_list.append(int(float(line.strip())))
    i = int(float(scored_list[0]))
else:
#if they havent create an empty list
    scored_list = np.zeros(len(data_list) + 1)
    i = 1

#Identifying data, user input controlled
while i != number_classifying + 1:
    print("\n")
    print('Entry number: ', i)
    print("0: Unrelated, 1: Current State, 2: Streaming/Youtube, 3: Professional, 4: Riot Art, 5: Skins, 6: Fan Art/Cosplay 7: Merchandise 8: Other")
    relevance_value = input(data_list[i] + ":\n")
    if relevance_value == 'instructions':
        exit_input = 0
        while exit_input == 0:
            print(instructions)
            instruct_input = input("Type 'Q' to exit instructions: ")
            if instruct_input == "Q" or instruct_input=="q":
                exit_input = 1
        instruct_input = 0
    else:
        #assigns a score to a tweet at the current index
        if ((relevance_value=='1') or (relevance_value=='0') or (relevance_value=='2') or (relevance_value=='3') or (relevance_value=='4') or (relevance_value=='5') or (relevance_value=='6') or (relevance_value=='7') or (relevance_value=='8')):
            scored_list[i]=relevance_value
            i += 1
        else:
            #shows the list of the current scores assigned
            if relevance_value == 'scores':
                print(scored_list)
            else:
                #quits the program
                if relevance_value == 'quit':
                    quit()
                else:
                    #Saves the user's place and allows them to start from where they left off
                    if relevance_value == 'save':
                        scored_list[0] = i
                        #saves the scores to a json
                        with open(save_filename, "w") as f:
                            for s in scored_list:
                                f.write(str(s) + "\n")
                        #saves the tweet list to a json
                        with open(champion_tweet_list_filename, "w", encoding="utf8") as f:
                            for s in data_list:
                                s = str(s)
                                s = str.replace(s, "\n", "")
                                f.write(s + "\n")
                    else:
                        #prints available commands for the user
                        if relevance_value == 'commands':
                            print("help, instructions, undo, save, quit, commands")
                        else:
                            #allows the user to undo a 1 or 0 input
                            if relevance_value =='undo':
                                scored_list[i-1] = 0
                                i = i-1
                            else:
                                #lets user see where to contact me for help
                                if relevance_value == 'help':
                                    print('Email me at aldurret@ncsu.edu or message me on slack @Adam Durrett(Partysquid) if you have any questions.')
                                else:
                                #all other inputs are invalid
                                    print("Invalid Input")
print(scored_list)
#saves i to index index
scored_list[0] = i
#saves tweets and scores in usable format for me to use for analysis
with open(save_filename, "w") as f:
    for s in scored_list:
        f.write(str(s) + "\n")
with open(champion_tweet_list_filename, "w", encoding="utf8") as data_list:
    for s in data_list:
        s = str(s)
        s = str.replace(s, "\n", "")
        data_list.write(s + "\n")

#end of program
print("Thank you for your help, please send this entire folder to Adam Durrett at aldurret@ncsu.edu")
print("Put the name of the champion and the partition number in the subject.")
quit()