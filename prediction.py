import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

#read data generated from ETL pipeline for Classification
file_classify_pollutant = "classify_pollutant.csv"
df_input = pd.read_csv(file_classify_pollutant, encoding = "utf-8", header = 0)

countAirPollutants = len(df_input[df_input.isAir == 1])
countAerosolPollutants = len(df_input[df_input.isAir == 0])
print("Percentage of Pollutants being assessed in Air: {:.2f}%".format((countAirPollutants / (len(df_input.isAir))*100)))
print("Percentage of Pollutants being assessed in Aerosol: {:.2f}%".format((countAerosolPollutants / (len(df_input.isAir))*100)))

#Creating Model
y = df_input['isAir']
X = df_input.drop(['isAir'], axis = 1)

#Split data to 70% train and 30% test
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=.3,random_state=42)

#scale the data
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_train = pd.DataFrame(X_train_scaled)

X_test_scaled = scaler.transform(X_test)
X_test = pd.DataFrame(X_test_scaled)

#Decision Tree
decisiontree = DecisionTreeClassifier()
decisiontree.fit(X_train, y_train)
y_pred = decisiontree.predict(X_test)
acc_decisiontree = round(accuracy_score(y_pred, y_test) * 100, 2)
print("Accuracy of Decision Tree: ",acc_decisiontree)

#Random Forest 
randomforest = RandomForestClassifier()
randomforest.fit(X_train, y_train)
y_pred = randomforest.predict(X_test)
acc_randomforest = round(accuracy_score(y_pred, y_test) * 100, 2)
print("Accuracy of Random Forest: ",acc_randomforest)

#Logistic Regression
logreg = LogisticRegression()
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)
acc_logreg = round(accuracy_score(y_pred, y_test) * 100, 2)
print("Accuracy of Logistic Regression: ",acc_logreg)