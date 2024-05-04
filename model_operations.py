from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, roc_curve, auc
import matplotlib.pyplot as plt
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

def train_random_forest(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    return model

def train_naive_bayes(X_train, y_train):
    model = GaussianNB()
    model.fit(X_train, y_train)  
    return model


def train_logistic_regression(X_train, y_train):
    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model

def train_svm(X_train, y_train):
    svm = SVC(kernel='linear', probability=True)  #'linear', 'rbf', 'poly'
    svm.fit(X_train, y_train)
    return svm

def predict(model, X_test):
    return model.predict(X_test)

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    # Binarize the labels for each class using one-hot encoding
    y_test_binarized = label_binarize(y_test, classes=model.classes_)
    
    # Define mappings for class labels to make it clearer
    class_mappings = {
        0: "0-1",
        1: "1-0",
        2: "1/2-1/2"
    }
    
    # Compute predicted probabilities for each class
    y_probs = model.predict_proba(X_test)
    
    # Compute ROC curve and AUC for each class
    plt.figure(figsize=(8, 6))
    for i in range(len(model.classes_)):
        fpr, tpr, _ = roc_curve(y_test_binarized[:, i], y_probs[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label='ROC curve (area = %0.2f) for %s' % (roc_auc, class_mappings[i]))
    
    # Plot ROC curve for random guessing
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    
    # Set plot labels and legend
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve for Multi-class')
    plt.legend(loc="lower right")
    plt.show()
    
    return accuracy

def tune_random_forest(X_train, y_train):
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 20],
        'min_samples_split': [2, 5, 10]
    }
    grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

def tune_logistic_regression(X_train, y_train):
    param_grid = {
        'C': [0.1, 1, 10],
        'penalty': ['l1', 'l2']
    }
    grid_search = GridSearchCV(LogisticRegression(), param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

def tune_svm(X_train, y_train):
    param_grid = {
        'kernel': ['linear', 'rbf', 'poly'],
        'C': [0.1, 1, 10],
        'gamma': ['scale', 'auto']
    }
    grid_search = GridSearchCV(SVC(probability=True), param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_
