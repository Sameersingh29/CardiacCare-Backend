# Clinician model
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split

class LWGMKNN:
    def __init__(self, k=5):
        self.k = k
        self.X_train = None
        self.y_train = None
        self.scaler = RobustScaler()

    def fit(self, X, y):
        # Scale the training data
        self.X_train = self.scaler.fit_transform(X)
        self.y_train = y

    def predict(self, X):
        # Scale the input data using the same scaler
        X_scaled = self.scaler.transform(X)
        predictions = []
        for test_instance in X_scaled:
            distances = self._compute_distances(test_instance)
            predictions.append(self._predict_class(distances))
        return np.array(predictions)

    def _compute_distances(self, test_instance):
        # Compute distances between test instance and training data
        distances = np.linalg.norm(self.X_train - test_instance, axis=1)
        return distances

    def _predict_class(self, distances):
        # Predict class based on nearest neighbors
        neighbors_idx = np.argsort(distances)[:self.k]
        neighbor_classes = self.y_train[neighbors_idx]
        lw = 1 / (distances[neighbors_idx] + 1e-9)
        gm = []
        
        for c in np.unique(self.y_train):
            if np.any(neighbor_classes == c):
                gm.append(np.mean(lw[neighbor_classes == c]))
            else:
                gm.append(0)
        
        return np.unique(self.y_train)[np.argmax(gm)]

# Load model
def load_model():
    base_dir = os.path.dirname(__file__)  # Directory containing this script
    file_path = os.path.join(base_dir, 'datasets', 'Clinical_database-1.csv')
    # Load your dataset
    df = pd.read_csv(file_path)
    
    # Prepare data
    X = df.drop(columns=["target"])
    y = df["target"]
    
    # Train model
    model = LWGMKNN(k=5)
    model.fit(X, y)
    
    return model, X.columns.tolist()

# Global model and feature names
CAD_MODEL, FEATURE_NAMES = load_model()

# Additional functions for evaluation can be added here
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def evaluate_model(model, X_test, y_test):
    # Make predictions on test data
    y_pred = model.predict(X_test)
    
    # Evaluate model performance
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")
    roc_auc = roc_auc_score(pd.get_dummies(y_test), pd.get_dummies(y_pred), multi_class="ovr")
    
    # Display performance metrics
    print("Accuracy:", accuracy * 100)
    print("Precision:", precision * 100)
    print("Recall:", recall * 100)
    print("F1-Score:", f1 * 100)
    print("ROC-AUC:", roc_auc * 100)

# Example usage
if __name__ == "__main__":
    # Load model and data
    model, feature_names = load_model()

    # Example test set (you can replace this with your own dataset)
    df = pd.read_csv('datasets/Clinical_database-1.csv')
    X = df[feature_names]  # Use feature names from the loaded model
    y = df["target"]

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate the model
    evaluate_model(model, X_test, y_test)
