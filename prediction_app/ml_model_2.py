# Patient Model

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import accuracy_score, classification_report

class LWGMKNN:
    def __init__(self, k=5, distance_metric='euclidean'):
        self.k = k
        self.X_train = None
        self.y_train = None
        self.distance_metric = distance_metric
        self.scaler = RobustScaler()
    
    def fit(self, X, y):
        # Ensure X is a DataFrame or convert it to one
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        # Scale the training data while preserving feature names
        self.X_train = pd.DataFrame(
            self.scaler.fit_transform(X), 
            columns=X.columns, 
            index=X.index
        )
        self.y_train = y
    
    def predict(self, X):
        # Ensure X is a DataFrame or convert it to one
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        # Scale test data using the same scaler, preserving feature names
        X_scaled = pd.DataFrame(
            self.scaler.transform(X), 
            columns=X.columns, 
            index=X.index
        )
        
        predictions = []
        for _, test_instance in X_scaled.iterrows():
            distances = self._compute_distances(test_instance.values)
            predictions.append(self._predict_class(distances))
        return np.array(predictions)
    
    def _compute_distances(self, test_instance):
        if self.distance_metric == 'euclidean':
            distances = np.linalg.norm(self.X_train.values - test_instance, axis=1)
        elif self.distance_metric == 'manhattan':
            distances = np.sum(np.abs(self.X_train.values - test_instance), axis=1)
        else:
            raise ValueError(f"Unsupported distance metric: {self.distance_metric}")
        return distances
    
    def _predict_class(self, distances):
        neighbors_idx = np.argsort(distances)[:self.k]
        neighbor_classes = self.y_train.iloc[neighbors_idx].values
        lw = 1 / (distances[neighbors_idx] + 1e-6)
        # Weighted geometric mean
        class_scores = {c: np.prod(lw[neighbor_classes == c]) for c in np.unique(self.y_train)}
        return max(class_scores, key=class_scores.get)
    
    def predict_proba(self, X):
        """
        Estimate prediction probabilities.
        """
        # Ensure X is a DataFrame or convert it to one
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        predictions = []
        for _, test_instance in X.iterrows():
            distances = self._compute_distances(test_instance.values)
            neighbors_idx = np.argsort(distances)[:self.k]
            neighbor_classes = self.y_train.iloc[neighbors_idx].values
            
            # Calculate proportion of positive class in neighborhood
            positive_ratio = np.mean(neighbor_classes)
            predictions.append([1 - positive_ratio, positive_ratio])
        
        return np.array(predictions)

def load_model():
    base_dir = os.path.dirname(__file__)  # Directory containing ml_model_2.py
    file_path = os.path.join(base_dir, 'datasets', 'cardio_train.csv')
    # Read the dataset
    df = pd.read_csv(file_path, sep=';')
    
    # Drop the ID column if it exists
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    
    target_column = 'cardio'
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Parameter grid for k
    param_grid = {'k': [3, 5, 7, 9]}
    best_k = 5
    best_accuracy = 0
    
    # Grid search for best k
    for k in param_grid['k']:
        model = LWGMKNN(k=k)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        # Print detailed classification report for each k
        # print(f"K = {k}")
        # print(classification_report(y_test, y_pred))
        
        if acc > best_accuracy:
            best_k = k
            best_accuracy = acc
    
    # print(f"Best K: {best_k}, Best Accuracy: {best_accuracy}")
    
    # Train final model with best k
    final_model = LWGMKNN(k=best_k)
    final_model.fit(X, y)
    
    return final_model, X.columns.tolist()

# Global model and feature names
CAD_MODEL_2, FEATURE_NAMES_2 = load_model()