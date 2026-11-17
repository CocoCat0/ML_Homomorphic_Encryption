import numpy as np
import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta
import hashlib


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"


def generate_telemetry(samples=100):

    np.random.seed(42)

    data = []

    process_names = [
        "browser.exe",
        "notepad.exe",
        "python.exe",
        "office.exe",
        "system_service.exe"
    ]

    event_types = [
        "PROCESS_EXECUTION",
        "LOGIN_SUCCESS",
        "LOGIN_FAILURE",
        "NETWORK_ACTIVITY",
        "SECURITY_ALERT"
    ]

    for i in range(samples):

        # Generate endpoint telemetry

        failed_logins = np.random.randint(0, 15)

        active_sessions = np.random.randint(1, 20)

        network_frequency = np.random.randint(1, 100)

        time_since_rotation = np.random.randint(1, 365)

        anomaly_score = np.random.uniform(0, 1)

        # Generate simulated process metadata

        process_name = np.random.choice(process_names)

        parent_process = np.random.choice(process_names)

        event_type = np.random.choice(event_types)

        # Generate a synthetic file hash

        hash_input = f"synthetic-file-{i}"

        file_hash = hashlib.sha256(
            hash_input.encode()
        ).hexdigest()

        # Generate simulated risk score

        risk_score = (
            failed_logins * 0.15 +
            active_sessions * 0.03 +
            network_frequency * 0.01 +
            time_since_rotation * 0.002 +
            anomaly_score * 2
        )

        # Assign risk classification

        if risk_score >= 5:

            severity = "HIGH"

            risk_label = "DANGER"

        elif risk_score >= 3.5:

            severity = "MEDIUM"

            risk_label = "ELEVATED"

        else:

            severity = "LOW"

            risk_label = "NORMAL"

        # Create synthetic endpoint event

        event = {

            "timestamp": (
                datetime(2026, 11, 16)
                - timedelta(seconds=i)
            ).isoformat(),

            "device_id": f"ENDPOINT-{i+1:03}",

            "hostname": f"WORKSTATION-{i+1:03}",

            "username": f"simulated_user{i+1:03}",

            "event_id": f"EVT-{i+1:05}",

            "event_type": event_type,

            "process_name": process_name,

            "parent_process": parent_process,

            "process_path": (
                f"C:/Synthetic/Applications/{process_name}"
            ),

            "command_line": (
                f"{process_name} --synthetic-event {i+1}"
            ),

            "user_sid": f"S-1-5-21-1000-{i+1}",

            "file_hash": file_hash,

            "failed_logins": failed_logins,

            "active_sessions": active_sessions,

            "network_frequency": network_frequency,

            "time_since_rotation": time_since_rotation,

            "anomaly_score": round(anomaly_score, 4),

            "risk_score": round(risk_score, 4),

            "severity": severity,

            "risk_label": risk_label

        }

        data.append(event)

    return pd.DataFrame(data)


def save_telemetry(samples=100):

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    telemetry = generate_telemetry(samples)

    output_file = DATA_DIR / "simulated_telemetry.csv"

    telemetry.to_csv(output_file, index=False)

    print("\nSynthetic EDR telemetry generated!")

    print("\nDataset preview:")

    print(telemetry.head())

    print(f"\nSaved to: {output_file}")

    return telemetry


if __name__ == "__main__":

    save_telemetry()

