import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Ensure directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('preprocessing', exist_ok=True)

def preprocess_data(filepath, sequence_length=10):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by engine_id and timestamp
    df = df.sort_values(['engine_id', 'timestamp'])
    
    # Handle missing values
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)
    
    # Feature Engineering
    # Encode categorical variables
    label_encoders = {}
    categorical_cols = ['engine_type', 'fuel_type', 'manufacturer', 'maintenance']
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
        joblib.dump(le, f'preprocessing/le_{col}.pkl')
    
    # Target Variable Encoding
    le_target = LabelEncoder()
    df['failure_mode_encoded'] = le_target.fit_transform(df['failure_mode'])
    joblib.dump(le_target, 'preprocessing/le_failure_mode.pkl')
    
    # Save the mapping for backend
    target_mapping = {int(k): str(v) for k, v in enumerate(le_target.classes_)}
    with open('models/class_mapping.json', 'w') as f:
        json.dump(target_mapping, f)
    
    # Select features for training
    features = [
        'engine_temperature', 'oil_pressure', 'fuel_pressure', 'vibration_level',
        'rpm', 'engine_load', 'coolant_temperature', 'exhaust_temperature',
        'running_period', 'fuel_consumption', 'engine_type', 'fuel_type',
        'manufacturer', 'maintenance'
    ]
    
    # Scale features
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])
    joblib.dump(scaler, 'preprocessing/scaler.pkl')
    
    # Generate sequences
    X, y = [], []
    for engine_id in df['engine_id'].unique():
        engine_df = df[df['engine_id'] == engine_id]
        
        # Check if enough data points for the sequence
        if len(engine_df) < sequence_length:
            continue
            
        feature_vals = engine_df[features].values
        target_vals = engine_df['failure_mode_encoded'].values
        
        for i in range(len(engine_df) - sequence_length):
            X.append(feature_vals[i:(i + sequence_length)])
            y.append(target_vals[i + sequence_length])
            
    X = np.array(X)
    y = np.array(y)
    
    print(f"Generated {len(X)} sequences of length {sequence_length}.")
    return X, y, len(le_target.classes_)

def build_model(input_shape, num_classes):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model():
    X, y, num_classes = preprocess_data('datasets/marine_engine_data.csv')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = build_model((X_train.shape[1], X_train.shape[2]), num_classes)
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint('models/marine_engine_model.keras', save_best_only=True, monitor='val_loss')
    ]
    
    print("Starting training...")
    history = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=20,
        batch_size=64,
        callbacks=callbacks
    )
    
    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
    
    model.save('models/marine_engine_model.keras')
    print("Model saved to models/marine_engine_model.keras")

if __name__ == '__main__':
    train_model()
