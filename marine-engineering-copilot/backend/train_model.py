import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(BASE_DIR, '..', 'dataset', 'manuals', 'marine_engine_data.csv')
MODEL_OUT = os.path.join(BASE_DIR, 'predictive_model.pkl')

def train():
    print(f"Loading data from {DATA_CSV}...")
    df = pd.read_csv(DATA_CSV)
    
    # Define features and target
    features = [
        'engine_temp', 'oil_pressure', 'vibration_level', 'rpm', 
        'engine_load', 'coolant_temp', 'exhaust_temp', 'running_period', 
        'fuel_consumption'
    ]
    target = 'failure_mode'
    
    # Drop rows with NaN in these columns just in case
    df = df.dropna(subset=features + [target])
    
    X = df[features]
    y = df[target]
    
    # Train-test split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training Random Forest on {len(X_train)} samples...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Save the model
    print(f"Saving model to {MODEL_OUT}...")
    # Save model and a list of feature names so we know the expected input order
    joblib.dump({"model": model, "features": features}, MODEL_OUT)
    print("Done!")

if __name__ == "__main__":
    train()
