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
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.datasets import make_regression
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier

print('--------START-------')
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

#10 Cross Fold Validation
print("--------------10 Fold ---------------------")
clf = svm.SVC(gamma='auto')
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.5, shuffle=True, random_state=2)
#clf = svm.SVC(kernel='linear', C=1)#, random_state=42); print ('svm - linear');

#clf = svm.SVC(gamma='auto')#(kernel='linear'); print ('svm - auto');
#clf = LogisticRegression(max_iter=1000)#dual=False); print ('LogisticRegression');
clf = ExtraTreesClassifier(); print ('ExtraTreesClassifier');
###clf = RandomForestRegressor(n_estimators = 1000)#, random_state = 42) print ('RandomForestRegressor');
###clf = Lasso(alpha=1.0) print ('Lasso');

Score_10Cross = cross_val_score(clf, X, y, cv=10)
print("10 cross_val_score : ", Score_10Cross)
print("%0.2f accuracy with a standard deviation of %0.2f" % (Score_10Cross.mean(), Score_10Cross.std()))

