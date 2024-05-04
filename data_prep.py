import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.impute import SimpleImputer

def load_data(filepath):
    try:
        # Try reading with default UTF-8 first
        return pd.read_csv(filepath)
    except UnicodeDecodeError:
        # If UTF-8 fails, try using a different encoding
        return pd.read_csv(filepath, encoding='ISO-8859-1')

def preprocess_data(df):

    # Drop rows with any missing values in order to fit for SMOTE
    df.dropna(inplace=True)

        # Drop the 'winner' column 
    df.drop(columns=['winner'], inplace=True)

    #df['winner'] = LabelEncoder().fit_transform(df['winner'])  # Assuming 'winner' is the problematic column

    df['opening'] = LabelEncoder().fit_transform(df['opening'])

    features = ['total_moves', 'opening', 'white_skill', 'black_skill', 'white_castled', 'black_castled', 'opposite_side_castle', 'white_sacrifices', 'black_sacrifices', 'w_knight_to_bishop', 'b_knight_to_bishop', 'white_piece_activity', 'black_piece_activity', 'eval_after_move_15']
    
    
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])
    return df

"""
def split_data(df):
    X = df.drop('result', axis=1)
    y = df['result']
    return train_test_split(X, y, test_size=0.25, random_state=11)
"""

def split_data(df):
    X = df.drop('result', axis=1)
    y = df['result']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=11)

    # Apply SMOTE to the training set 
    smote = SMOTE(random_state=11)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

    return X_train_smote, X_test, y_train_smote, y_test

