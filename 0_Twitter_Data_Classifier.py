import pandas as pd
import numpy as np
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import Helper_Functions as hf
import re
import time
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://LOLread:"+'LaberLabsLOLquery'+"@lolsql.stat.ncsu.edu/lol")

#////PROGRAM PARAMETERS////
wk_dir ='C:\\Users\\Adam Durrett\\Documents\\GitHub\\sentiment_analysis\\Data\\'
n_parts = 10 #number of partitions in training dataframe
n_features = 2000
void_champs = ["Cho'Gath", "Kha'Zix", "Rek'Sai", "Kog'Maw", "Vel'Koz"]
vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=n_features, stop_words= 'english')
partition_list = [0,1,2,3,4,5,6,7,8,9]

#////IMPORTED DATA////
start_import = time.time()
bad_text_list = hf.json_to_textlist(wk_dir + 'RandomTweets.json')
print("Time for importing randomtweets: " + str(time.time() - start_import))

start_import = time.time()
data_set = pd.read_pickle(wk_dir + 'Champions_df.pickle')
#data_set = pd.read_sql('select * from championstwitter limit 1000000', engine)
print("Time for reading dataframe(2.19): " + str(time.time() - start_import))
data_set = data_set.drop_duplicates(subset = "Text", keep = "last")
print("Time for importing dataframe(3.6): " + str(time.time() - start_import))


########################################################################################################################
#////FUNCTIONS////

#Input: List of Trainers
#Output: List of Trainers without testers
#Format:
def refine_trainer(train_list):
    start = time.time()
    train_list = train_list[n_tests:]
    print("Time for refine_trainer: " + str(time.time() - start))
    return train_list

#Input: Name of champ, text string
#Output: Text string with name of champ removed
def reg_remove_name(text_string):
    for name in void_champs:
        myRe = re.compile(name[0:3] + " " + name[4:], re.IGNORECASE)
        text_string = myRe.sub('', text_string)
        myRe = re.compile(name[0:3] + "['`_\-" + name[4:] + "’´]*[ !,.?\-_&$x" + name[:-1] + "`'’´\b]", re.IGNORECASE)
        text_string = myRe.sub('', text_string)
        myRe = re.compile(name[4:] + "*[ !,.?\-_`'’´&$\b]", re.IGNORECASE)
        text_string = myRe.sub('', text_string)
    return text_string

#Input: Dataframe, Void Champion Name List
#Output: Same dataframe with void champion name removed from ['Text'] in all possible formats
#Format: dataframe is Adam's format, Void champion list is just a list of void champions
def remove_voidchamp_text(dataframe):
    start = time.time()
    dataframe['newText'] = dataframe['Text'].apply(reg_remove_name)
    dataframe['oldText'] = dataframe['Text']
    dataframe['Text'] = dataframe['newText']
    dataframe = dataframe.drop(columns = 'newText')
    print("Time for remove_voidchamp_text: " + str(time.time() - start))
    return dataframe


#Input: List that has positive valued text, list that has negative valued text.
#  In this case positive is related, negative unrelated
#Output: Model trained on the 2 inputs.
#Format: each list is a list of strings.
def train_classifier(pos_list, neg_list):
    start = time.time()
    print("!Positive List Length:")
    print(len(pos_list))
    print("!Negative List Length:")
    print(len(neg_list))
    y_value_list = list(np.ones(len(pos_list))) + list(np.zeros(len(neg_list)))
    x_list = pos_list + neg_list

    x_data = vectorizer.fit_transform(x_list)

    clf = LogisticRegression()

    model = clf.fit(x_data, y_value_list)
    print("Time for train_classifier: " + str(time.time() - start))
    return model

#Input:
#Output:
#This function takes the champion dataframe, and the random tweets list and combines it into one dataframe
# it has the partition, text, and relevance values, which can be easily turned into lists to train the data.
def create_training_testing_df(good_df, bad_list):
    start = time.time()
    dataframe = good_df[good_df['Name'].isin(void_champs)].copy()
    dataframe = remove_voidchamp_text(dataframe)
    dataframe = dataframe.filter(['Text', 'oldText'], axis = 1)
    dataframe['Relevance'] = 1

    bad_list = bad_list[0:len(dataframe)]
    bad_df = pd.DataFrame({"Text":bad_list, "Relevance":0})


    frames = [dataframe, bad_df]
    new_df = pd.concat(frames)
    new_df['Partition'] = np.random.choice(range(n_parts), len(new_df))
    print("Time for create_training_testing_df: " + str(time.time() - start))
    return new_df

def test_data(good_tester, bad_tester, model):
    start = time.time()
    test_ones = list(np.ones(len(good_tester)))
    test_zeros = list(np.zeros(len(bad_tester)))

    n_tests = len(good_tester)+len(bad_tester)

    test_relevances = test_ones + test_zeros
    test_texts = good_tester + bad_tester

    tester = vectorizer.transform(test_texts)
    tested_values = model.predict(tester)
    comparison = sum(tested_values == test_relevances) / (n_tests)

    confidence = model.predict_proba(tester)

    print(comparison)
    print("Time for test_data: " + str(time.time() - start))
    return([tested_values, comparison, confidence])

#Input: model testing
#Output: Dataframe with top words and their values of the classifier
#This function will gather the top words of the classifier and give us them in a dataframe with their predicted labels
def get_top_words(model):
    start = time.time()
    indices = np.argsort(vectorizer.idf_)[::-1]
    features = vectorizer.get_feature_names()
    top_features = [features[i] for i in indices[:n_features]]
    print(top_features)

    transformed_top_features = vectorizer.transform(top_features)

    top_feature_labels = model.predict(transformed_top_features)
    prediction_probabilities = model.predict_proba(transformed_top_features)

    predprob_0 = []
    predprob_1 = []

    start2 = time.time()
    for i in prediction_probabilities:
        predprob_0.append(i[0])
        predprob_1.append(i[1])
    top_words_df = pd.DataFrame({"Top_Word":top_features,
                                 "Label":top_feature_labels,
                                 "Pred Prob is 0": predprob_0,
                                 "Pred Prob is 1": predprob_1})
    print("Time for get_top_words prediction probability(0.0): " + str(time.time() - start2))
    print("Time for get_top_words: " + str(time.time() - start))
    return(top_words_df)

#Input: dataframe of tweets, with training values and partitions, number of partition being used for testing
#output: tested prediction portion of DF
#This function takes the input of the dataframe, and runs training on every partition except the input #
#It will return the test with the accuracy of it identifying on the testing data.
def run_partition(df, partition_num):
    start = time.time()
    good_test_list = list(new_df[(new_df['Partition'] == partition_num) &
                                 (new_df['Relevance'] == 1)]['Text'].values)
    bad_test_list = list(new_df[(new_df['Partition'] == partition_num) &
                                (new_df['Relevance'] == 0)]['Text'].values)

    train_df = new_df[(new_df['Partition'] != partition_num)]
    good_train_list = list(new_df[(new_df['Partition'] != partition_num) &
                                  (new_df['Relevance'] == 1)]['Text'].values)
    bad_train_list = list(new_df[(new_df['Partition'] != partition_num) &
                                 (new_df['Relevance'] == 0)]['Text'].values)

    model = train_classifier(good_train_list, bad_train_list)
    test_it = test_data(good_test_list, bad_test_list, model)

    print(common_member(good_test_list, good_train_list))
    print(common_member(bad_test_list, bad_train_list))
    print("Time for run_partition: " + str(time.time() - start))
    return(test_it)

#Tells if there is a common string between list a and b--- Chris thinks there's a built in function for this
#input: 2 lists of strings
#output: true or false
def common_member(a, b):
    start = time.time()
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        print("Time for common_member: " + str(time.time() - start))
        return "THERE ARE MATCHES IN THESE SETS"
    else:
        print("Time for common_member: " + str(time.time() - start))
        return False

#Predicts labels of a list-- MAIN CLASSIFICATION
#Input: List of strings, Model
#Output: Predicted labels
def predict_on_list(list, model):
    start = time.time()
    transformed_list = vectorizer.transform(list)
    prediction_confidence = model.decision_function(transformed_list)
    print(prediction_confidence)
    print("Time for predict_on_list: " + str(time.time() - start))
    return(model.predict(transformed_list))

#Runs training and testing on each partition
#Input: Dataframe with training/testing data
#Output: Dataframe with predicted values and accuracy
def run_on_partitions(df):
    start = time.time()
    accuracy = 0
    for i in partition_list:
        predict_partition = run_partition(df, i)
        df.loc[df.Partition == i, 'Predicted_Value'] = predict_partition[0]

        predprob_of_0 = []
        predprob_of_1 =[]

        for x in predict_partition[2]:
            predprob_of_0.append(x[0])
            predprob_of_1.append(x[1])

        print(len(df.loc[df.Partition == i]))
        df.loc[df.Partition == i, 'Pred Prob of 0'] = predprob_of_0
        df.loc[df.Partition ==i, 'Pred Prob of 1'] = predprob_of_1
        accuracy = accuracy + predict_partition[1]

    print("Accuracy of Model: ", accuracy/len(partition_list))
    print("Time for run_on_partitions: " + str(time.time() - start))
    return df
########################################################################################################################
#This section prepares the void champion sections of the data frame to be passed as training data
main_start = time.time()
new_df = create_training_testing_df(data_set, bad_text_list)
new_df = new_df.drop_duplicates(subset = 'Text', keep = 'last')

new_df = run_on_partitions(new_df)


final_model = train_classifier(list(new_df[new_df['Relevance'] == 1]['Text'].values),
                               list((new_df[new_df['Relevance'] == 0]['Text'].values)))
tester = list(data_set['Text'].values)

data_set['Relevance'] = predict_on_list(tester, final_model)

data_set = data_set.loc[data_set['Relevance']==1]

top_words_df = get_top_words(final_model)


#Printing the percentage that is True Positive, False Positive, True Negative and False Negative
#TP = real is 1 and predicted is 1, TN = real is 0 and predicted is 0
#FP = real is 1 and predicted is 0, FN = real is 0 and predicted is 1
true_pos_perc = (len(new_df.loc[(new_df['Relevance'] == 1) & (new_df['Predicted_Value'] == 1)]))/len(new_df)
print('True Positive: ' + str(true_pos_perc*100) + "%")
true_neg_perc = (len(new_df.loc[(new_df['Relevance'] == 0) & (new_df['Predicted_Value'] == 0)]))/len(new_df)
print('True Negative: ' + str(true_neg_perc*100) + "%")
false_pos_perc = (len(new_df.loc[(new_df['Relevance'] == 1) & (new_df['Predicted_Value'] == 0)]))/len(new_df)
print('False Positive: ' + str(false_pos_perc*100) + "%")
false_neg_perc = (len(new_df.loc[(new_df['Relevance'] == 0) & (new_df['Predicted_Value'] == 1)]))/len(new_df)
print('False Negative: ' + str(false_neg_perc*100) + "%")

#Printing top 10 words for each label
top_words_1 = top_words_df.loc[top_words_df['Label'] == 1]
top_words_0 = top_words_df.loc[top_words_df['Label'] == 0]

print(top_words_1['Top_Word'].values)
print(top_words_0['Top_Word'].values)

top_words_1.to_csv('top_words_1.csv')
top_words_0.to_csv('top_words_0.csv')
print("Time for main_function: " + str(time.time() - main_start))
# ######## NOTES?///////////////////
# #
# # figure out what to do next