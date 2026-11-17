#import the function from the server folder, under file encrypted inference
from server.encrypted_inference import encrypted_inference

#this function will be utilized to have the ML process the encrypted requests
def process_encrypted_request(public_context_bytes, encrypted_telemetry_bytes, weights, bias):
    print("\n========== ML SERVER ==========")
    print("Encrypted telemetry received.")
    print("Processing encrypted ML inference...")

    encrypted_result = encrypted_inference(
        public_context_bytes,
        encrypted_telemetry_bytes,
        weights,
        bias
    )

    print("Encrypted result generated.")
    print("Sending encrypted result back to device.")

    return encrypted_result

