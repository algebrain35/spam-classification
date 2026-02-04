import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve,precision_score, recall_score, confusion_matrix, accuracy_score
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
from typing import Optional

class SpamDetectionModel:
    def __init__(self, clf=LogisticRegression, from_file=False, filepath: Optional[str] = None):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        if not from_file:
            self.set_classifier(clf)
        else:
            if filepath == None:
                raise ValueError("Error: Filepath is empty")
            self.load_model_from_file(filepath)
        self.dataset = pd.DataFrame()
        self.is_vectorizer_fitted = False
        self._init_prod()
    def set_classifier(self, clf, **kwargs):
        self.classifier = clf()
    def load_model_from_file(self, filepath):
        try:
            self.classifier = joblib.load(filepath)
        except:
            pass
    def _init_prod(self):
        self.load_dataset("Phishing_Email.csv")
        X_train, X_test, y_train, y_test = self.preprocess('Email Text', 'Email Type')
        self.train(X_train, y_train)
    def export_to_pkl(self, filepath):
        joblib.dump(self.classifier, filepath)
    def load_dataset(self, csv_path):
        self.dataset = pd.read_csv(csv_path)
    def fit_vectorizer(self, X):
        self.is_vectorizer_fitted = True
        return self.vectorizer.fit_transform(X)
    def preprocess(self, text_col, target_col, split=0.2):
        data = self.dataset[text_col].fillna('')
        target = self.dataset[target_col]
        
        data_train, data_test, y_train, y_test = train_test_split(data, target, test_size=split, random_state=42)

        X_train = self.fit_vectorizer(data_train)
        X_test = self.transform(data_test)

        return X_train, X_test, y_train, y_test
    def transform(self, X):
        if not self.is_vectorizer_fitted:
            raise RuntimeError("Vectorizer has not been fitted")
        return self.vectorizer.transform(X)
    def train(self, X, y):
        self.classifier.fit(X, y)
    def predict(self, test):
        return self.classifier.predict(test)
    def predict_proba(self, test):
        return self.classifier.predict_proba(test)
    def benchmark(self, X_test, y_test):
        y_preds = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_preds)
        precision = precision_score(y_test, y_preds, zero_division=0)
        recall = recall_score(y_test, y_preds, zero_division=0) 
        return f'''
        Accuracy: f{accuracy}
        Precision: f{precision}
        Recall: f{recall}
        '''
    def score(self, test, target):
        return self.classifier.score(test, target)
    def calculate_youden(self, X_test, y_test):
        probs = self.predict_proba(X_test)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_test, probs)

        youden = tpr - fpr
        optimal = np.argmax(youden)

        return optimal
    def set_thresholds(self, t_low, t_high):
        self.threshold_cold = t_low
        self.threshold_hot = t_high
    def find_thresholds(self, y_true, y_probs, target_precision=0.95, target_npv=0.95):
        t_space = np.linspace(0, 1, 100)
        t_low = None
        t_high = None

        for t in t_space:
            preds = (y_probs >= t).astype(int)
            precision = precision_score(y_true, preds, zero_division=0)

            if precision >= target_precision:
                t_high = t
                break
        for t in reversed(t_space):
            preds = (y_probs >= t).astype(int)
            tn = np.sum((preds == 0) & (y_true == 0))
            fn = np.sum((preds == 0) & (y_true == 1))

            npv = tn / (tn + fn) if (tn + fn) > 0 else 0

            if npv >= target_npv:
                t_low = t
                break
        t_low = t_low if t_low != None else 0.0 
        t_high = t_high if t_high != None else 1.0

        if t_low > t_high:
            mid = t_low + (t_low - t_high) / 2
            t_low = mid - 0.1
            t_high = mid + 0.1
        return t_low, t_high
    def assign_tier_score(self, y_preds, t_low, t_high):
        conditions = [
            y_preds < t_low,
            (y_preds >= t_low) & (y_preds <= t_high),
            y_preds > t_high
        ]

        tiers = ["cold", "warm", "hot"]

        return np.select(conditions, tiers, default="")

model = SpamDetectionModel(from_file=True, filepath="spam.pkl")
model.load_dataset("Phishing_Email.csv")
X_train, X_test, y_train, y_test = model.preprocess('Email Text', 'Email Type')
preds = model.predict_proba(X_test)[:, 1]
tiers = model.assign_tier_score(preds, 0.5, 0.6)



        

