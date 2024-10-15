import os
import operator
from pickle import TRUE
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn import metrics
from matplotlib import style
import svm_data_prep  as sdp
style.use("ggplot")
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_validate
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import recall_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LassoCV
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt

from collections import defaultdict, Counter


#code_acc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Accessible_Code.csv', 'code_acc', True)
#code_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Code.csv', 'code_inacc')
#code_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Code_second_run.csv', 'code_inacc', True)
#code_data_org = pd.concat([code_acc, code_inacc], axis=0)

code_data_org = sdp.get_prep_data(r'C:\PHD\Classifier\Data\Version_4_GumTree_Integrated\code_31_july_2022\code.csv', 'code', True)#, True)
print(code_data_org.shape)
code_type, code_data = sdp.get_clean_data(code_data_org)
#code_data.to_csv('code_data.csv')  

#test_acc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Accessible_Test.csv', 'test_acc', True)
#test_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Test.csv', 'test_inacc')
#test_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Test_second_run.csv', 'test_inacc', True)
#test_data_org = pd.concat([test_acc, test_inacc], axis=0)
test_data_org = sdp.get_prep_data(r'C:\PHD\Classifier\Data\Version_4_GumTree_Integrated\test_31_july_2022\test.csv', 'test', True)#, True)
print(test_data_org.shape)
test_type, test_data = sdp.get_clean_data(test_data_org)

#test_data.to_csv('test_data.csv')  

#build_acc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Accessible_Build.csv', 'build_acc')
#build_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Build.csv', 'build_inacc')
#build_data_org = pd.concat([build_acc, build_inacc], axis=0)
#build_type, build_data = sdp.get_clean_data(build_data_org)
#buil_data.to_csv('buil_data.csv')  


X = pd.concat([code_data, test_data])#, build_data], axis=0)
y = pd.concat([code_type, test_type])#, build_type], axis=0)
print("--------------Data Shape---------------------")
print(X.shape, y.shape)

print("--------------train_test_split---------------------")
scores = []
mScores = []
cScores = []
tScores = []
bScores = []
featuresList = []

isPd = False;

iterations = 10

for i in range (0,iterations):
    print('Iteration : ', i)

    test_size = 0.1;
    print("Train size : ", 1 - test_size, "Test Size : ", test_size) 
       
    #Code sampling
    cX_train, cX_test, cY_train, cY_test = train_test_split(code_data, code_type, test_size=test_size, random_state=i)
    print("Code Bugs Shape : ", cX_train.shape, cX_test.shape, cY_train.shape, cY_test.shape)    

    #Data sampling    
    tX_train, tX_test, tY_train, tY_test = train_test_split(test_data, test_type, test_size=test_size, random_state=i)  
    print("Test Bugs Shape : ", tX_train.shape, tX_test.shape, tY_train.shape, tY_test.shape)      
      
    X_train = pd.concat([cX_train, tX_train], axis=0) 
    X_test = pd.concat([cX_test, tX_test], axis=0)     

    y_train = pd.concat([cY_train, tY_train], axis=0) 
    y_test = pd.concat([cY_test, tY_test], axis=0)  
    print()

    clf = ExtraTreesClassifier()#n_estimators = 1000).fit(X, y)
    clf.fit(X_train, y_train)   

    features = {}
    features = dict(zip( X.columns.tolist(), clf.feature_importances_.tolist()))
    featuresList.append(features)
    #print(clf.feature_importances_, X.columns)

    #feat_importances = pd.Series(clf.feature_importances_, index=X.columns)
    #feat_importances.nlargest(10).plot(kind='barh')
    #plt.show()    

    mscore =  round(clf.score(X_test, y_test), 2)
    print("Mix score : ", mscore)
    mScores.append(mscore)

    cScore =  round(clf.score(cX_test, cY_test), 2)
    print("code score : ", cScore)            
    cScores.append(cScore)    

    tScore =  round(clf.score(tX_test, tY_test),2)
    print("test score : ", tScore)  
    tScores.append(tScore)             
    print("-----------------")

print("Average mScore : ",  round(sum(mScores) / len(mScores), 2), mScores)
print("Average cScore : ",  round(sum(cScores) / len(cScores), 2), cScores)
print("Average tScore : ",  round(sum(tScores) / len(tScores), 2), tScores)

df = pd.DataFrame(featuresList)
df = df.append(pd.Series(df.sum(),name='Total'))

df.to_csv('res.csv')

featureDict = (df.iloc[-1]).to_dict()

#featureDict_v1 = {}
#for x, y in featureDict.items():
#    if y != 0:
#        featureDict_v1[x] = y

featureDict_Rank = sorted(featureDict.items(), key=operator.itemgetter(1), reverse=True)

df = pd.DataFrame(featureDict_Rank)
df[1] = df[1]/ iterations
df = df.append(pd.Series(df.sum(),name='Total'))
df = df.sort_values(by=[1], ascending=False)


print(df)



 
