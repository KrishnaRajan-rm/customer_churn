from sklearn.linear_model import LogisticRegression
from  sklearn.model_selection import train_test_split,cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score,confusion_matrix,classification_report
import pandas as pd
import os
import joblib


dataset=pd.read_csv("customer_ml_features.csv")

y=dataset["churn"]

x=dataset.drop(columns=["customer_id","churn","tenure_bucket"])

x=pd.get_dummies(x,columns=["contract","internet_service"],drop_first=False)

X_train ,X_test,Y_train,Y_test=train_test_split(x,y,test_size=0.2,stratify=y,random_state=42)

logistic_model=LogisticRegression(max_iter=50)
decision_tree=DecisionTreeClassifier(max_depth=5,random_state=42)

logistic_model.fit(X_train,Y_train)
decision_tree.fit(X_train,Y_train)


logistic_predictions=logistic_model.predict(X_test)
decision_tree_predictions=decision_tree.predict(X_test)


print("\n="+ "="*59)
print("LOGISTIC REGRESSION")
print("="*60)
 
print("Classification Report")
print(classification_report(
         Y_test,
         logistic_predictions,
         target_names = ["Active","Churned"]
     )
      )
 
print("\n="+ "="*59)
print("DECISION TREE CLASSIFIER")
print("="*60)
 
print("Classification Report")
print(classification_report(
         Y_test,
         decision_tree_predictions,
         target_names = ["Active","Churned"]
     )
      )

print("\n="+ "="*59)
print("Accuracy Scores")
print("="*60)

la=accuracy_score(Y_test, logistic_predictions)
da=accuracy_score(Y_test, decision_tree_predictions)

print("Logistic Regression Accuracy:",la)
print("Decision Tree Accuracy:",da)

print("\n="+ "="*59)
print("Precision_Scores")
print("="*60)

lp=precision_score(Y_test, logistic_predictions)
dp=precision_score(Y_test, decision_tree_predictions)   

print("Logistic Regression Precision:",lp)
print("Decision Tree precision:",dp)

print("\n="+ "="*59)
print("F1_Scores")
print("="*60)

lf1=f1_score(Y_test, logistic_predictions)
df1=f1_score(Y_test, decision_tree_predictions)

print("Logistic Regression F-1 Score:",lf1)
print("Decision Tree F-1 Score:",df1)


os.makedirs("./models",exist_ok=True)

joblib.dump(logistic_model,"./models/logistic_model.pkl")
joblib.dump(decision_tree,"./models/decision_tree_model.pkl")




