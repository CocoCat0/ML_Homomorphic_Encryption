import pandas as pd
import numpy as np
import joblib
import time

from pathlib import Path

from device.encryption import (
    create_encryption_context,
    encrypt_telemetry,
    create_public_context
)

from device.decryption import decrypt_prediction
from key_management.rotation_policy import rotation_policy
from server.model_training import train_model
from server.ml_server import process_encrypted_request


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "simulated_telemetry.csv"
SERVER_DIR = BASE_DIR / "server"
RESULTS_DIR = BASE_DIR / "results"

FEATURES = [
    "failed_logins",
    "active_sessions",
    "network_frequency",
    "time_since_rotation",
    "anomaly_score"
]

RECORDS_TO_PROCESS = 50

CONFIGURATIONS = {
    "Configuration A (8192)": 8192,
    "Configuration B (16384)": 16384
}


def evaluate_configuration(
    configuration_name,
    degree,
    data,
    scaler,
    weights,
    bias
):

    print("\n==============================================")
    print(configuration_name)
    print("==============================================")

    total_start = time.perf_counter()

    # ----------------------------------
    # INITIAL CKKS CONTEXT
    # ----------------------------------

    context_start = time.perf_counter()

    context = create_encryption_context(degree)

    public_context_bytes = create_public_context(context)

    initial_context_time = (
        time.perf_counter() - context_start
    )

    encryption_times = []
    inference_times = []
    decryption_times = []
    numerical_errors = []
    ciphertext_sizes = []

    rotation_times = []

    rotation_counts = {
        "NORMAL": 0,
        "ELEVATED": 0,
        "HIGH": 0
    }

    # ----------------------------------
    # PROCESS TELEMETRY
    # ----------------------------------

    for index, row in data.iterrows():

        print(
            f"\nProcessing telemetry record "
            f"{index + 1}/{len(data)}"
        )

        telemetry = row[FEATURES].to_numpy(dtype=float)

        normalized = scaler.transform(
            pd.DataFrame([telemetry], columns=FEATURES)
        )[0]

        # Plaintext prediction

        plaintext_prediction = float(
            np.dot(normalized, weights) + bias
        )

        # ----------------------------------
        # ENCRYPTION
        # ----------------------------------

        encryption_start = time.perf_counter()

        encrypted_data = encrypt_telemetry(
            context,
            normalized
        )

        encrypted_data_bytes = encrypted_data.serialize()

        encryption_time = (
            time.perf_counter() - encryption_start
        )

        encryption_times.append(encryption_time)

        ciphertext_sizes.append(
            len(encrypted_data_bytes)
        )

        # ----------------------------------
        # ENCRYPTED INFERENCE
        # ----------------------------------

        inference_start = time.perf_counter()

        encrypted_result = process_encrypted_request(
            public_context_bytes,
            encrypted_data_bytes,
            weights,
            bias
        )

        inference_time = (
            time.perf_counter() - inference_start
        )

        inference_times.append(inference_time)

        # ----------------------------------
        # DECRYPTION
        # ----------------------------------

        decryption_start = time.perf_counter()

        prediction = decrypt_prediction(
            context,
            encrypted_result
        )

        decryption_time = (
            time.perf_counter() - decryption_start
        )

        decryption_times.append(decryption_time)

        # ----------------------------------
        # NUMERICAL ERROR
        # ----------------------------------

        numerical_error = abs(
            plaintext_prediction - prediction
        )

        numerical_errors.append(numerical_error)

        print("\nPlaintext score:", plaintext_prediction)
        print("Encrypted score:", prediction)
        print("Numerical error:", numerical_error)

        # ----------------------------------
        # KEY ROTATION POLICY
        # ----------------------------------

        print("\n========== KEY ROTATION EVALUATION ==========")

        action = rotation_policy(prediction)

        rotation_counts[action] += 1

        # ----------------------------------
        # PERFORM KEY ROTATION
        # ----------------------------------

        if action in ["ELEVATED", "HIGH"]:

            print("\n========== PERFORMING KEY ROTATION ==========")

            rotation_start = time.perf_counter()

            new_context = create_encryption_context(degree)

            new_public_context_bytes = create_public_context(
                new_context
            )

            rotation_time = (
                time.perf_counter() - rotation_start
            )

            rotation_times.append(rotation_time)

            # Replace the active context

            context = new_context

            public_context_bytes = new_public_context_bytes

            print("\nNew encryption context generated.")
            print("Previous context replaced.")

            print(
                f"Key rotation completed in "
                f"{rotation_time:.6f} seconds"
            )

        else:

            print("\nNo key rotation required.")

    # ----------------------------------
    # TOTAL EXECUTION TIME
    # ----------------------------------

    total_execution_time = (
        time.perf_counter() - total_start
    )

    # ----------------------------------
    # ROTATION STATISTICS
    # ----------------------------------

    total_rotations = len(rotation_times)

    total_rotation_time = sum(rotation_times)

    average_rotation_time = (
        np.mean(rotation_times)
        if rotation_times else 0
    )

    rotation_overhead = (
        (total_rotation_time / total_execution_time) * 100
        if total_execution_time > 0 else 0
    )

    # ----------------------------------
    # PERFORMANCE RESULTS
    # ----------------------------------

    results = {

        "Configuration": configuration_name,

        "Records processed": len(data),

        "Average encryption time": np.mean(encryption_times),

        "Average inference time": np.mean(inference_times),

        "Average decryption time": np.mean(decryption_times),

        "Average numerical error": np.mean(numerical_errors),

        "Average ciphertext size": np.mean(ciphertext_sizes),

        "Initial context generation time": initial_context_time,

        "Key rotations performed": total_rotations,

        "Average key rotation time": average_rotation_time,

        "Total key rotation time": total_rotation_time,

        "Key rotation overhead (%)": rotation_overhead,

        "Total execution time": total_execution_time,

        "NORMAL decisions": rotation_counts["NORMAL"],

        "ELEVATED decisions": rotation_counts["ELEVATED"],

        "HIGH decisions": rotation_counts["HIGH"]

    }

    return results


# ==============================================
# FINAL KEY ROTATION CONCLUSIONS
# ==============================================

def display_conclusions(results_df):

    print("\n")
    print("=" * 65)
    print("          KEY ROTATION PERFORMANCE ANALYSIS")
    print("=" * 65)

    for _, row in results_df.iterrows():

        print("\n" + str(row["Configuration"]))

        print("-" * 55)

        print(
            "Records processed:",
            row["Records processed"]
        )

        print(
            "Key rotations performed:",
            row["Key rotations performed"]
        )

        print(
            "Average key rotation time:",
            f'{row["Average key rotation time"]:.6f} seconds'
        )

        print(
            "Total key rotation time:",
            f'{row["Total key rotation time"]:.6f} seconds'
        )

        print(
            "Key rotation overhead:",
            f'{row["Key rotation overhead (%)"]:.2f}%'
        )

        print(
            "NORMAL decisions:",
            row["NORMAL decisions"]
        )

        print(
            "ELEVATED decisions:",
            row["ELEVATED decisions"]
        )

        print(
            "HIGH decisions:",
            row["HIGH decisions"]
        )

    # ----------------------------------
    # COMPARE CONFIGURATIONS
    # ----------------------------------

    print("\n")
    print("=" * 65)
    print("                FINAL CONCLUSIONS")
    print("=" * 65)

    config_a = results_df.iloc[0]
    config_b = results_df.iloc[1]

    # Key rotation performance

    print("\n1. KEY ROTATION PERFORMANCE:")

    if (
        config_a["Average key rotation time"]
        <
        config_b["Average key rotation time"]
    ):

        print(
            "Configuration A demonstrated faster "
            "average key rotation."
        )

    elif (
        config_b["Average key rotation time"]
        <
        config_a["Average key rotation time"]
    ):

        print(
            "Configuration B demonstrated faster "
            "average key rotation."
        )

    else:

        print(
            "Both configurations demonstrated equal "
            "average key rotation time."
        )

    # Computational efficiency

    print("\n2. COMPUTATIONAL EFFICIENCY:")

    if (
        config_a["Total execution time"]
        <
        config_b["Total execution time"]
    ):

        print(
            "Configuration A completed the evaluation "
            "with lower total execution time."
        )

    else:

        print(
            "Configuration B completed the evaluation "
            "with lower total execution time."
        )

    # Numerical accuracy

    print("\n3. NUMERICAL ACCURACY:")

    if (
        config_a["Average numerical error"]
        <
        config_b["Average numerical error"]
    ):

        print(
            "Configuration A achieved lower average "
            "numerical error."
        )

    else:

        print(
            "Configuration B achieved lower average "
            "numerical error."
        )

    # Key rotation overhead

    print("\n4. KEY ROTATION OVERHEAD:")

    if (
        config_a["Key rotation overhead (%)"]
        <
        config_b["Key rotation overhead (%)"]
    ):

        print(
            "Configuration A experienced lower "
            "key rotation overhead."
        )

    else:

        print(
            "Configuration B experienced lower "
            "key rotation overhead."
        )

    # Security policy

    print("\n5. SECURITY POLICY:")

    print(
        "NORMAL predictions maintain the existing "
        "rotation schedule."
    )

    print(
        "ELEVATED predictions trigger increased "
        "key rotation frequency."
    )

    print(
        "HIGH predictions trigger immediate "
        "key replacement."
    )

    print(
        "\nNote: These are experimental policy decisions. "
        "They do not independently establish security."
    )

    print("\n" + "=" * 65)

    print("       END OF PERFORMANCE EVALUATION")

    print("=" * 65)


# ==============================================
# MAIN PROGRAM
# ==============================================

def main():

    print("\n==============================================")
    print(" PRIVACY-PRESERVING MACHINE LEARNING SYSTEM ")
    print(" CKKS PERFORMANCE EVALUATION ")
    print("==============================================")

    # ----------------------------------
    # STEP 1: LOAD TELEMETRY
    # ----------------------------------

    print("\nSTEP 1: LOADING TELEMETRY")

    if not DATA_FILE.exists():

        from device.telemetry import save_telemetry

        save_telemetry(samples=100)

    data = pd.read_csv(DATA_FILE)

    if len(data) < RECORDS_TO_PROCESS:

        raise ValueError(
            f"Dataset must contain at least "
            f"{RECORDS_TO_PROCESS} records."
        )

    data = data.iloc[:RECORDS_TO_PROCESS].reset_index(drop=True)

    print("Records selected:", len(data))

    # ----------------------------------
    # STEP 2: LOAD ML MODEL
    # ----------------------------------

    print("\nSTEP 2: LOADING MACHINE LEARNING MODEL")

    required_files = [

        SERVER_DIR / "model.pkl",

        SERVER_DIR / "scaler.pkl",

        SERVER_DIR / "model_weights.npy",

        SERVER_DIR / "model_bias.npy"

    ]

    if not all(file.exists() for file in required_files):

        print("Model files missing. Training model...")

        train_model()

    scaler = joblib.load(
        SERVER_DIR / "scaler.pkl"
    )

    weights = np.load(
        SERVER_DIR / "model_weights.npy"
    )

    bias = float(
        np.load(SERVER_DIR / "model_bias.npy")
    )

    print("Model successfully loaded.")

    # ----------------------------------
    # STEP 3: RUN CONFIGURATION TESTS
    # ----------------------------------

    print("\nSTEP 3: STARTING CKKS COMPARISON")

    all_results = []

    for configuration_name, degree in CONFIGURATIONS.items():

        results = evaluate_configuration(
            configuration_name,
            degree,
            data,
            scaler,
            weights,
            bias
        )

        all_results.append(results)

    results_df = pd.DataFrame(all_results)

    # ----------------------------------
    # STEP 4: DISPLAY PERFORMANCE RESULTS
    # ----------------------------------

    print("\n==============================================")

    print(" CKKS PERFORMANCE EVALUATION RESULTS ")

    print("==============================================")

    display_columns = [

        "Configuration",

        "Records processed",

        "Average encryption time",

        "Average inference time",

        "Average decryption time",

        "Average numerical error",

        "Average ciphertext size",

        "Initial context generation time",

        "Key rotations performed",

        "Average key rotation time",

        "Total key rotation time",

        "Key rotation overhead (%)",

        "Total execution time"

    ]

    print(
        results_df[display_columns].to_string(
            index=False
        )
    )

    # ----------------------------------
    # STEP 5: DISPLAY KEY ROTATION CONCLUSIONS
    # ----------------------------------

    display_conclusions(results_df)

    # ----------------------------------
    # STEP 6: SAVE RESULTS
    # ----------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        RESULTS_DIR / "ckks_performance_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print("\nResults saved to:")

    print(output_file)

    print("\n==============================================")

    print(" EVALUATION COMPLETED SUCCESSFULLY ")

    print("==============================================")


if __name__ == "__main__":
    main()

