#import needed libraries for the model training
import pandas as pd
import numpy as np
import joblib

from pathlib import Path

#Machine learning models from sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, classification_report)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "simulated_telemetry.csv"
SERVER_DIR = BASE_DIR / "server"

#Features the machine learning model will oversee
FEATURES = [
    "failed_logins",
    "active_sessions",
    "network_frequency",
    "time_since_rotation",
    "anomaly_score"
]


def train_model():

    SERVER_DIR.mkdir(parents=True, exist_ok=True)

    # Load telemetry
    data = pd.read_csv(DATA_FILE)

    X = data[FEATURES]

    # Generate simulated risk labels
    risk_score = (
        X["failed_logins"] * 0.15 +
        X["active_sessions"] * 0.03 +
        X["network_frequency"] * 0.01 +
        X["time_since_rotation"] * 0.002 +
        X["anomaly_score"] * 2
    )

    y = (risk_score >= 3.5).astype(int)

    print("\n========== MODEL TRAINING ==========")

    print("Total samples:", len(X))

    print("Normal samples:", sum(y == 0))

    print("Elevated samples:", sum(y == 1))

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Normalize features
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)

    X_test_scaled = scaler.transform(X_test)

    # Train evaluation model
    evaluation_model = LinearSVC(
        random_state=42,
        max_iter=10000
    )

    evaluation_model.fit(
        X_train_scaled,
        y_train
    )

    predictions = evaluation_model.predict(
        X_test_scaled
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\nModel accuracy:", accuracy)

    print("\nClassification report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    # Train final model using all data
    final_scaler = StandardScaler()

    X_scaled = final_scaler.fit_transform(X)

    final_model = LinearSVC(
        random_state=42,
        max_iter=10000
    )

    final_model.fit(X_scaled, y)

    # Save model and scaler
    joblib.dump(
        final_model,
        SERVER_DIR / "model.pkl"
    )

    joblib.dump(
        final_scaler,
        SERVER_DIR / "scaler.pkl"
    )

    # Extract linear model parameters
    np.save(
        SERVER_DIR / "model_weights.npy",
        final_model.coef_[0]
    )

    np.save(
        SERVER_DIR / "model_bias.npy",
        final_model.intercept_[0]
    )

    print("\nModel successfully trained and saved!")

    print("Model weights:", final_model.coef_[0])

    print("Model bias:", final_model.intercept_[0])

    return final_model, final_scaler


if __name__ == "__main__":

    train_model()

