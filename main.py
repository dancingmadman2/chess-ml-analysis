from data_prep import load_data, preprocess_data, split_data
from model_operations import train_random_forest, train_naive_bayes, train_logistic_regression, train_svm, evaluate_model
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score
import numpy as np
import pandas as pd





def plot_feature_importance(model, X_train):
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(10, 6))
    plt.title("Feature Importance")
    plt.bar(range(X_train.shape[1]), importances[indices], align="center")
    plt.xticks(range(X_train.shape[1]), X_train.columns[indices], rotation=90)
    plt.tight_layout()
    plt.show()

def plot_manual_feature_importance(coefficients, feature_names):
    feat_importances = pd.Series(coefficients, index=feature_names)
    feat_importances.nlargest(20).plot(kind='barh', title='Feature Importance')
    plt.xlabel('Coefficient Magnitude')
    plt.ylabel('Feature')
    plt.show()

def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['White wins', 'Black wins', 'Draw'], yticklabels=['White wins', 'Black wins', 'Draw'])
    plt.title('Detailed Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.show()




def print_classification_report(y_true, y_pred):
    report = classification_report(y_true, y_pred)
    print(report)


def main():
    df = load_data('chess_games_dataset_2500.csv')
    df = preprocess_data(df)
    X_train, X_test, y_train, y_test = split_data(df)
    
    model = train_svm(X_train, y_train)
    #accuracy = evaluate_model(model, X_test, y_test)
    predictions = model.predict(X_test)
    plot_confusion_matrix(y_test, predictions)
    #plot_feature_importance(model,X_train)
    plot_manual_feature_importance(model.coef_[0], X_train.columns)    
    print_classification_report(y_test, predictions)

    accuracy = evaluate_model(model,X_test,y_test)
    
    print(f'Accuracy on test data: {accuracy}')

if __name__ == '__main__':
    main()

