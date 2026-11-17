import tenseal as ts
import numpy as np


def encrypted_inference(
    public_context_bytes,
    encrypted_telemetry_bytes,
    weights,
    bias
):

    # Reconstruct public encryption context
    context = ts.context_from(
        public_context_bytes
    )

    # Reconstruct encrypted telemetry
    encrypted_data = ts.ckks_vector_from(
        context,
        encrypted_telemetry_bytes
    )

    # Validate model parameters
    weights = np.asarray(weights, dtype=float)

    if weights.shape != (5,):
        raise ValueError("Expected exactly 5 model weights.")

    if not np.all(np.isfinite(weights)):
        raise ValueError("Model weights contain invalid values.")

    if not np.isfinite(bias):
        raise ValueError("Model bias contains an invalid value.")


    # Calculate encrypted weighted sum
    encrypted_score = encrypted_data.dot(
        weights.tolist()
    )

    # Add model bias
    encrypted_score = encrypted_score + float(bias)

    print("\nEncrypted inference completed!")

    print("Server processed encrypted telemetry.")

    # Return encrypted decision score
    return encrypted_score.serialize()
