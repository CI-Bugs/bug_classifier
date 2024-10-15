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
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_validate
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_validate
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import recall_score
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.datasets import make_regression
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn import linear_model
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.metrics import classification_report
#code_acc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Accessible_Code.csv', 'code_acc', True)
#code_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Code.csv', 'code_inacc')
#code_inacc = sdp.get_prep_data('C:\PHD\Classifier\Data\Version_2\Inaccessible_Code_second_run.csv', 'code_inacc', True)
#code_data_org = pd.concat([code_acc, code_inacc], axis=0)

print('--------START-------')
#code_data_org = sdp.get_prep_data(r'C:\Users\vkabadi\OneDrive - The University of Melbourne\Vinay\PHD\GIT\bug_classifier\Bugs_Classification\data\code_31_july_2022\code.csv', 'code', True, 211)
#code_data_org = sdp.get_prep_data(r'C:\Users\vkabadi\OneDrive - The University of Melbourne\Vinay\PHD\2_Research_Work\Classifier\Data\Version_6_23Aug2024\codeResults\code
code_data_org = sdp.get_prep_data(r'C:\Users\vkabadi\OneDrive - The University of Melbourne\Vinay\PHD\2_Research_Work\Classifier\Data\Version_4_GumTree_Integrated\code_31_july_2022\code.csv', 'code', True)#, 211)
print(code_data_org.shape)
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
#build_data_org = pd.concat([build_acc, build_inacc], axis=0)
#build_type, build_data = sdp.get_clean_data(build_data_org)
#buil_data.to_csv('buil_data.csv')  


X = pd.concat([code_data, test_data])#, build_data], axis=0)
y = pd.concat([code_type, test_type])#, build_type], axis=0)
print("--------------Data Shape---------------------")
print(X.shape, y.shape)

print("--------------train_test_split---------------------")

mScores = []
mAccs   = []
mRecalls= []
mPrecs  = []

cScores = []
cAccs   = []
cRecalls= []
cPrecs  = []

tScores = []
tAccs   = []
tRecalls= []
tPrecs  = []


for i in range (1,10):

    test_size = 0.1;
    print("Train size : ", 1 - test_size, "Test Size : ", test_size) 
       
    #Code sampling
    cX_train, cX_test, cY_train, cY_test = train_test_split(code_data, code_type, test_size=test_size)#, random_state=i)
    print("Code Bugs Shape : ", cX_train.shape, cX_test.shape, cY_train.shape, cY_test.shape)    

    #Data sampling    
    tX_train, tX_test, tY_train, tY_test = train_test_split(test_data, test_type, test_size=test_size)#, random_state=i)  
    print("Test Bugs Shape : ", tX_train.shape, tX_test.shape, tY_train.shape, tY_test.shape)      
      
    X_train = pd.concat([cX_train, tX_train], axis=0) 
    X_test = pd.concat([cX_test, tX_test], axis=0)     

    y_train = pd.concat([cY_train, tY_train], axis=0) 
    y_test = pd.concat([cY_test, tY_test], axis=0)  

    clf = svm.SVC(gamma='auto'); print ('svm - auto'); #(kernel='linear')
    #clf = LogisticRegression(max_iter=1000)#dual=False); print ('LogisticRegression');
    #clf = ExtraTreesClassifier(); print ('ExtraTreesClassifier');
    #clf = SGDClassifier();#loss="hinge", penalty="l2", max_iter=5)
    #clf = make_pipeline(StandardScaler(), SVC())

    ##### Not Good
    #clf = RandomForestRegressor(n_estimators = 1000)#, random_state = 42) print ('RandomForestRegressor');
    #clf = Lasso(alpha=1.0); print ('Lasso');
    #clf = svm.SVR()
    #clf = linear_model.BayesianRidge()


    clf.fit(X_train, y_train)     
    '''
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
    '''

    print("Mix Data : ")
    y_pred=clf.predict(X_test);

    mScore  = round(clf.score(X_test, y_test), 2);
    mAcc    = round(metrics.accuracy_score(y_test, y_pred));
    mRecall = round(metrics.recall_score(y_test, y_pred, zero_division=1), 2);
    mPrec   = round(metrics.precision_score(y_test, y_pred, zero_division=1), 2);


    mScores.append(mScore)       
    mAccs.append(mAcc)           
    mRecalls.append(mRecall)      
    mPrecs.append(mPrec)    

    
    print('mScore : ',mScore)
    print('mAccuracy: ', mAcc)
    print('mRecall: ', mRecall)
    print('mPrecision: ', mPrec)
    print('mReport: ',metrics.classification_report(y_test, y_pred, zero_division=1))
    
    
    print("Code Data : ")
    cY_pred=clf.predict(cX_test)

    cScore  = round(clf.score(cX_test, cY_test), 2);
    cAcc    = round(metrics.accuracy_score(cY_test, cY_pred), 2)
    cRecall = round(metrics.recall_score(cY_test, cY_pred, zero_division=1), 2)
    cPrec   = round(metrics.precision_score(cY_test, cY_pred, zero_division=1), 2)

    cScores.append(cScore)       
    cAccs.append(cAcc)           
    cRecalls.append(cRecall)      
    cPrecs.append(cPrec)    


    
    print('cScore : ',cScore)
    print('cAccuracy: ',cAcc)
    print('cRecall: ',cRecall)
    print('cPrecision: ',cPrec)
    print('cReport: ',metrics.classification_report(cY_test, cY_pred, zero_division=1))         
    

    print("Test Data : ")
    tY_pred=clf.predict(tX_test)

    tScore  = round(clf.score(tX_test, tY_test), 2)
    tAcc    = round(metrics.accuracy_score(tY_test, tY_pred), 2)
    tRecall = round(metrics.recall_score(tY_test, tY_pred, zero_division=1))
    tPrec   = round(metrics.precision_score(tY_test, tY_pred, zero_division=1), 2)


    tScores.append(tScore)       
    tAccs.append(tAcc)           
    tRecalls.append(tRecall)      
    tPrecs.append(tPrec)   
     
    
    print('tScore : ',tScore)
    print('tAccuracy: ',tAcc)
    print('tRecall: ',tRecall)
    print('tPrecision: ',tPrec)
    print('tReport: ',metrics.classification_report(tY_test, tY_pred, zero_division=1))        
    

               
mFinalScore  = round(sum(mScores)   / len(mScores)  , 2);
mFinalAcc    = round(sum(mAccs)     / len(mAccs)    , 2);
mFinalRecall = round(sum(mRecalls)  / len(mRecalls) , 2);
mFinalPrec   = round(sum(mPrecs)    / len(mPrecs)   , 2);
mF1          = round(2 * (mFinalPrec * mFinalRecall) / (mFinalPrec + mFinalRecall), 2);

cFinalScore  = round(sum(cScores)   / len(cScores)  , 2);
cFinalAcc    = round(sum(cAccs)     / len(cAccs)    , 2);
cFinalRecall = round(sum(cRecalls)  / len(cRecalls) , 2);
cFinalPrec   = round(sum(cPrecs)    / len(cPrecs)   , 2);
cF1          = round(2 * (cFinalPrec * cFinalRecall) / (cFinalPrec + cFinalRecall), 2);

tFinalScore  = round(sum(tScores)   / len(tScores)  , 2);
tFinalAcc    = round(sum(tAccs)     / len(tAccs)    , 2);
tFinalRecall = round(sum(tRecalls)  / len(tRecalls) , 2);
tFinalPrec   = round(sum(tPrecs)    / len(tPrecs)   , 2);
tF1          = round(2 * (tFinalPrec * tFinalRecall) / (tFinalPrec + tFinalRecall), 2);

avg_FinalScore  =  round(((cFinalScore + tFinalScore) / 2)   , 2);
avg_FinalAcc    =  round(((cFinalAcc + tFinalAcc) / 2)   , 2);
avg_FinalRecall =  round(((cFinalRecall + tFinalRecall) / 2)   , 2);
avg_FinalPrec   =  round(((cFinalPrec + tFinalPrec) / 2)   , 2);
avg_F1          =  round(((cF1 + tF1) / 2)   , 2);

print('----Mix------')
print("mix Final Score : ",  mFinalScore)
print("mix Final Accuracy : ",  mFinalAcc)
print("mix Final Recall : ",  mFinalRecall)    
print("mix Final Precision : ",  mFinalPrec)
print("mix F1 : ",  mF1)
print('----Code------')
print("code Final Score : ",  cFinalScore)
print("code Final Accuracy : ",  cFinalAcc)
print("code Final Recall : ",  cFinalRecall)    
print("code Final Precision : ",  cFinalPrec)
print("code F1 : ",  cF1)
print('----Test------')
print("test Final Score : ",  tFinalScore)
print("test Final Accuracy : ",  tFinalAcc)
print("test Final Recall : ",  tFinalRecall)    
print("test Final Precision : ",  tFinalPrec)
print("test F1 : ",  tF1)
print('----Avg------')
print("Average Final Score : ",  avg_FinalScore)
print("Average Final Accuracy : ",  avg_FinalAcc)
print("Average Final Recall : ",  avg_FinalRecall)    
print("Average Final Precision : ",  avg_FinalPrec)
print("Average F1 : ",  avg_F1)
