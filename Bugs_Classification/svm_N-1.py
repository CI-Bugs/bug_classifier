import os
from pickle import TRUE
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn import metrics
from matplotlib import style
import svm_data_prep  as sdp
style.use("ggplot")
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)

from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_validate
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LassoCV
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn import linear_model
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

def extractTestCodeResults(ListPred, ListAcctual):
    cBugsMatched  = 0
    cBugsUnMatched  = 0
    tBugsMatched  = 0
    tBugsUnMatched  = 0
    listZip = zip(ListPred, ListAcctual)
    for item in listZip:
        if item[0] == item[1]:
            if(item[0] == 1):
                cBugsMatched = cBugsMatched + 1
            else:
                tBugsMatched = tBugsMatched + 1
        else:
            if(item[0] == 1):
                cBugsUnMatched = cBugsUnMatched + 1
            else:
                tBugsUnMatched = tBugsUnMatched + 1
    return cBugsMatched, cBugsUnMatched, tBugsMatched, tBugsUnMatched


print('--------START-------')
code_data_org = sdp.get_prep_data(r'C:\Users\vkabadi\OneDrive - The University of Melbourne\Vinay\PHD\2_Research_Work\Classifier\Data\Version_4_GumTree_Integrated\code_31_july_2022\code.csv', 'code', True)#, 211)
code_type, code_data = sdp.get_clean_data(code_data_org)
#code_data.to_csv('code_data.csv')  

#test_acc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Accessible_Test.csv', 'test_acc', True)
#test_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Test.csv', 'test_inacc')
#test_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Test_second_run.csv', 'test_inacc', True)
#test_data_org = pd.concat([test_acc, test_inacc], axis=0)
test_data_org = sdp.get_prep_data(r'C:\Users\vkabadi\OneDrive - The University of Melbourne\Vinay\PHD\2_Research_Work\Classifier\Data\Version_4_GumTree_Integrated\test_31_july_2022\test.csv', 'test', True)#, 211)
print(test_data_org.shape)
test_type, test_data = sdp.get_clean_data(test_data_org)
#test_data.to_csv('test_data.csv')   

#build_acc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Accessible_Build.csv', 'build_acc')
#build_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Build.csv', 'build_inacc')

#data = pd.concat([code_acc, code_inacc, test_acc, test_inacc])#, build_acc,  build_inacc], axis=0)
data = pd.concat([code_data_org, test_data_org])#, build_acc,  build_inacc], axis=0)
data[['ProjName', 'Commit_ID']] = data['COMMIT'].str.split('_', expand=True)

commit_list = data['COMMIT'] # Set target as Category of Bug
commit_proj_list = sdp.split_list(commit_list, "_")
commit_proj_list_unq = set(commit_proj_list)

gen_scores      = []
acc_scores      = []

res_dict_proj   = {}
res_dict_perc   = {}

bugsCommit      = []
bugsScore       = []

bugsCnt         = []

cBugsCnt        = []
cBugsMatched    = []
cBugsUnMatched  = []
cBugsScore      = []

tBugsCnt        = []
tBugsMatched    = []
tBugsUnMatched  = []
tBugsScore      = []

for commit in commit_proj_list_unq:
    data_train = data[data['ProjName'] != commit]
    data_test = data.loc[data['ProjName'] == commit]

    data_train = data_train.drop(['ProjName', 'Commit_ID'], axis = 1)# Remove  target Category of Bug
    data_test = data_test.drop(['ProjName', 'Commit_ID'], axis = 1)# Remove  target Category of Bug    

    train_y, train_x = sdp.get_clean_data(data_train)
    test_y, test_x = sdp.get_clean_data(data_test) 
    print("--------------",commit,"---------------------")
    print(train_x.shape, train_y.shape)
    print(test_x.shape, test_y.shape)    

    #clf = svm.SVC(gamma='auto'); print ('svm - auto'); #(kernel='linear')
    #clf = LogisticRegression(max_iter=1000)#dual=False); print ('LogisticRegression');
    #clf = ExtraTreesClassifier(); print ('ExtraTreesClassifier');
    #clf = SGDClassifier();#loss="hinge", penalty="l2", max_iter=5)
    clf = make_pipeline(StandardScaler(), SVC())

    ##### Not Good
    #clf = RandomForestRegressor(n_estimators = 1000)#, random_state = 42) print ('RandomForestRegressor');
    #clf = Lasso(alpha=1.0); print ('Lasso');
    #clf = svm.SVR()
    #clf = linear_model.BayesianRidge()
    
    clf.fit(train_x, train_y) 
    score =  clf.score(test_x, test_y)
    print("Score : ", score)    
    bugsScore.append(score)

    pred_res = clf.predict(test_x)
    print("Pred Results : ", list(pred_res))
    print("Test Results : ", list(test_y))
    res = extractTestCodeResults(pred_res, test_y)
    #print("cBugsMatched: ", res[0], "cBugsUnMatched: ", res[1], "tBugsMatched: ", res[2], "tBugsUnMatched: ", res[3])
    bugsCommit.append(commit)
    cBugsMatched.append(res[0])
    cBugsUnMatched.append(res[1])
    cBugsCnt.append(res[0]+ res[1])

    tBugsMatched.append(res[2])
    tBugsUnMatched.append(res[3])     
    tBugsCnt.append(res[2]+ res[3])    

    bugsCnt.append(len(pred_res))

    try:
        cBugsScore.append(res[0] /  (res[0] + res[1]))       
    except:
        cBugsScore.append(0)       

    try:
        tBugsScore.append(res[2] /  (res[2] + res[3]))    
    except:
        tBugsScore.append(0)    

       

    res_dict_proj[commit] = score
    #res_dict_perc[acc_score].append(commit)
    try:
        res_dict_perc[score].append(commit)
    except KeyError:
        res_dict_perc[score] = [commit]    
#print("-------------")
#print("res_dict_proj : ", dict( sorted(res_dict_proj.items(), key=operator.itemgetter(1),reverse=True)))
print("-------------")
print("res_dict_perc : ", dict( sorted(res_dict_perc.items(), key=operator.itemgetter(0),reverse=True)))
print("-------------")
print("bugsCommit ", "bugsScore ", "bugsCnt ", "cBugsCnt ", "cBugsMatched ", "cBugsUnMatched ", "cBugsScore ", "tBugsCnt ", "tBugsMatched ", "tBugsUnMatched ", "tBugsScore ")
for index in range(0, len(bugsCommit)):
    print(bugsCommit[index], round(bugsScore[index],2), bugsCnt[index], cBugsCnt[index], cBugsMatched[index], cBugsUnMatched[index], round(cBugsScore[index],2), tBugsCnt[index], tBugsMatched[index], tBugsUnMatched[index], round(tBugsScore[index], 2))
    
print("-------------")
print("Avg Generic score : %0.2f " % (sum(bugsScore) / len(bugsScore)))


