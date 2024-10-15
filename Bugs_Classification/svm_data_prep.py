import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn import metrics
from matplotlib import style
style.use("ggplot")
import json

def get_prep_data(path, bug_type = '', rand_shuffle =  False, samples = 0, export_checksum = False):

    data_org   = pd.read_csv(path)

    #Add Checksum
    col_names = list(data_org.columns)
    col_names.remove('COMMIT')
    col_names.remove('Category')
    col_names.remove('NCF')

    data_org['CHECKSUM'] = data_org[col_names].sum(axis=1)
    
    ''' Use the NCF Files category
    ncf_df = pd.DataFrame(columns=['.xml','.yml','.json'])
    for (i,r) in data_org.iterrows():
        ncf_data = r['NCF']
        ncf_data = ncf_data.replace("\'", "\"")
        df1 = json.loads(ncf_data)
        #df1= pd.DataFrame([ncf_data],columns=["NCF"])

        temp_data = [df1.get('.xml', '0'), df1.get('.yml', '0'),df1.get('.json', '0')]
        ncf_df.loc[i] = temp_data
        
    data_org = pd.concat([data_org, ncf_df], axis=1)
    '''

    if(export_checksum):
        path_temp = path[:]
        path_split = path_temp.split("\\")
        path_new = path.replace(path_split[-1], 'chksm_'+bug_type+'.csv')
        data_org.to_csv(path_new)

    #Clean by removing empty data
    data_new = data_org[data_org['CHECKSUM'] != 0]

    #Random Shuffle to extract mixed data
    if(rand_shuffle):
        data_new = data_new.sample(frac=1, random_state = 52).reset_index(drop=True)
        print("Random Shuffled")    

    commits = {}
    for cmt in data_new['COMMIT']:
        key = cmt.split("_")[0]
        if key in commits:
            commits[key] += 1
        else:
            commits[key] = 1

    for k, v in commits.items():
        if v >= 10:
            print(k, v)            
    #print 
    print(bug_type + ' Bugs : Tot Bugs = ', len(data_org), ' Used Bugs = ', len(data_new), ' : ', len(data_new) / len(data_org) * 100, "%")
    #for item in data_new:
    #    print (item)

    return data_new

def get_clean_data(data):


    category = data['Category'] # Set target as Category of Bug
    clean_data = data.drop(['Category', 'COMMIT', 'NCF', 'CHECKSUM'], axis = 1)# Remove  target Category of Bug

    return category, clean_data


def split_list(lines, seperator):
    newlist = []
    for word in lines:
        word = word.split(seperator)
        newlist.append(word[0])  
    return newlist


def cutdown_code_samples(data):
    commits = {}

    '''
    for cmt in data['COMMIT']:
        key = cmt.split("_")[0]
        if key in commits:
            commits[key] += 1
        else:
            commits[key] = 1
    '''

    rem_data = {}
    rem_data['okhttp'] = 11
    rem_data['traccar'] = 31
    rem_data['byte-buddy'] = 59
    rem_data['Nukkit'] = 10
    rem_data['Baragon'] = 22
    '''
    Code
    okhttp 21 - 11
    traccar 31 - 17
    byte-buddy 59 - 33
    Nukkit 10 - 5
    Baragon 22  - 11

    Test
    retrofit 16
    byte-buddy 21
    okhttp 33
    traccar 13
    acs-aem-commons 10
    '''
    largest = {}
    for k, v in commits.items():
        if v >= 10:
            print(k, v)
    return data_new

def cutdown_test_samples(data):  
    return data